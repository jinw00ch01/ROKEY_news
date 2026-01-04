from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Analysis, Article, Source
from app.schemas import AnalyzeRequest
from app.services.analyzer import AnalyzerClient
from app.services.rss import NormalizedArticle, fetch_multiple
from app.utils.text import clean_html

logger = logging.getLogger(__name__)


def _ensure_sources(db: Session, feeds: list[tuple[str, str]]) -> dict[str, Source]:
    existing = db.query(Source).all()
    by_url = {s.url: s for s in existing}
    for url, name in feeds:
        if url in by_url:
            continue
        src = Source(name=name, url=url, active=True)
        db.add(src)
        db.flush()
        by_url[url] = src
    db.commit()
    return by_url


def _upsert_article(db: Session, source: Source, item: NormalizedArticle) -> Article | None:
    found = db.query(Article).filter(Article.hash == item.hash).one_or_none()
    if found:
        return None
    article = Article(
        source_id=source.id,
        title=item.title,
        link=item.link,
        published_at=item.published_at,
        content_raw=item.content,
        content_clean=clean_html(item.content),
        hash=item.hash,
    )
    db.add(article)
    db.flush()
    return article


async def run_ingest(db: Session) -> dict[str, int]:
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not set, analysis will be skipped.")
    feeds_env = settings.__dict__.get("rss_sources") or []
    if isinstance(feeds_env, str):
        feeds = json.loads(feeds_env)
    else:
        feeds = feeds_env
    feeds_tuples: list[tuple[str, str]] = []
    for feed in feeds:
        if isinstance(feed, dict):
            url = feed.get("url")
            name = feed.get("name") or url
        else:
            url = str(feed)
            name = str(feed)
        if url:
            feeds_tuples.append((url, name))

    if not feeds_tuples:
        return {"fetched": 0, "analyzed": 0}

    sources = _ensure_sources(db, feeds_tuples)
    fetched_items = await fetch_multiple(feeds_tuples)
    analyzer = AnalyzerClient(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    fetched_count = 0
    analyzed_count = 0

    name_to_source = {src.name: src for src in sources.values()}

    for item in fetched_items:
        src = name_to_source.get(item.source_name) or next(iter(sources.values()))
        article = _upsert_article(db, src, item)
        if not article:
            continue
        fetched_count += 1
        if analyzer and article.content_clean:
            req = AnalyzeRequest(
                article={
                    "title": article.title,
                    "content": article.content_clean,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "source": src.name,
                },
                need_keywords=True,
            )
            try:
                result = await analyzer.analyze(req)
                analysis = Analysis(
                    article_id=article.id,
                    summary=result.summary,
                    sentiment_label=result.sentiment.label,
                    sentiment_score=result.sentiment.score,
                    keywords=result.keywords,
                    json_meta={"reason": result.reason, "safety": result.safety_flag},
                    model_name="gemini-1.5-flash",
                )
                db.add(analysis)
                analyzed_count += 1
            except Exception as exc:  # pragma: no cover - 모니터링 목적
                logger.exception("Analyze failed: %s", exc)
        db.commit()

    return {"fetched": fetched_count, "analyzed": analyzed_count}

