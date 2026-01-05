from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, or_, String
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Analysis, Article, Source
from app.schemas import AnalysisOut, ArticleDetail, ArticleListResponse

router = APIRouter(prefix="/articles", tags=["articles"])


DbDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=ArticleListResponse)
def list_articles(
    db: DbDep,
    q: Optional[str] = Query(None, description="검색어"),
    sentiment: Optional[str] = Query(None, description="positive|neutral|negative"),
    source: Optional[str] = Query(None, description="source name"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    sort: str = Query("published_desc", description="published_desc|score_desc"),
):
    query = (
        db.query(Article, Analysis, Source)
        .join(Source, Source.id == Article.source_id, isouter=True)
        .join(Analysis, Analysis.article_id == Article.id, isouter=True)
    )

    conditions = []
    if q:
        like = f"%{q}%"
        # 제목, 본문, 키워드에서 검색
        search_conditions = [
            func.lower(Article.title).like(func.lower(like)),
            func.lower(Article.content_clean).like(func.lower(like)),
            # 키워드 배열을 텍스트로 변환하여 검색 (PostgreSQL & SQLite 호환)
            func.cast(Analysis.keywords, String).like(like),
        ]
        conditions.append(or_(*search_conditions))
    if sentiment:
        conditions.append(Analysis.sentiment_label == sentiment)
    if source:
        like_source = f"%{source}%"
        conditions.append(func.lower(Source.name).like(func.lower(like_source)))
    if from_date:
        conditions.append(Article.published_at >= from_date)
    if to_date:
        conditions.append(Article.published_at <= to_date)

    if conditions:
        query = query.filter(and_(*conditions))

    if sort == "score_desc":
        query = query.order_by(desc(Analysis.sentiment_score).nullslast())
    else:
        query = query.order_by(desc(Article.published_at).nullslast())

    items = []
    for art, ana, src in query.all():
        items.append(
            {
                "id": art.id,
                "title": art.title,
                "link": art.link,
                "published_at": art.published_at,
                "summary": getattr(ana, "summary", None),
                "sentiment_label": getattr(ana, "sentiment_label", None),
                "sentiment_score": getattr(ana, "sentiment_score", None),
                "keywords": getattr(ana, "keywords", None),
            }
        )
    return {"items": items}


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: DbDep):
    article = (
        db.query(Article)
        .options(joinedload(Article.analysis))
        .filter(Article.id == article_id)
        .one_or_none()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    ana = article.analysis
    return {
        "id": article.id,
        "title": article.title,
        "link": article.link,
        "published_at": article.published_at,
        "summary": ana.summary if ana else None,
        "sentiment_label": ana.sentiment_label if ana else None,
        "sentiment_score": ana.sentiment_score if ana else None,
        "keywords": ana.keywords if ana else None,
        "source_id": article.source_id,
    }


@router.get("/{article_id}/analysis", response_model=AnalysisOut)
def get_article_analysis(article_id: int, db: DbDep):
    ana = db.query(Analysis).filter(Analysis.article_id == article_id).one_or_none()
    if not ana:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return ana

