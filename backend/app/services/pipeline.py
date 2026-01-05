from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Analysis, Article, Source
from app.schemas import AnalyzeRequest
from app.services.analyzer import AnalyzerClient
from app.services.news_fetcher import NormalizedArticle, fetch_all_news
from app.utils.text import clean_html

logger = logging.getLogger(__name__)


def _ensure_sources(db: Session) -> Dict[str, Source]:
    """
    finnhub와 newsdata 소스가 DB에 존재하는지 확인하고, 없으면 생성합니다.
    """
    existing = db.query(Source).all()
    by_name = {s.name: s for s in existing}
    
    # finnhub 소스 확인
    if "finnhub" not in by_name:
        src = Source(name="finnhub", api_type="finnhub", active=True)
        db.add(src)
        db.flush()
        by_name["finnhub"] = src
    
    # newsdata 소스 확인
    if "newsdata" not in by_name:
        src = Source(name="newsdata", api_type="newsdata", active=True)
        db.add(src)
        db.flush()
        by_name["newsdata"] = src
    
    db.commit()
    return by_name


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
    
    # API 키가 없으면 종료
    if not settings.finnhub_api_key and not settings.newsdata_api_key:
        logger.warning("No news API keys configured")
        return {"fetched": 0, "analyzed": 0}

    sources = _ensure_sources(db)
    
    # finnhub와 NEWSDATA.io에서 뉴스 수집
    fetched_items = await fetch_all_news(settings.finnhub_api_key, settings.newsdata_api_key)
    
    analyzer = AnalyzerClient(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    fetched_count = 0
    analyzed_count = 0

    for item in fetched_items:
        # source_name 파싱 (예: "finnhub:general", "newsdata:kr")
        api_type = item.source_name.split(":")[0]
        src = sources.get(api_type)
        
        if not src:
            # 기본값으로 첫 번째 소스 사용
            src = next(iter(sources.values()))
        
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
