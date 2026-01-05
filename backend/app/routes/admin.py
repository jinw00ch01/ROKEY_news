from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, Analysis, Source
from app.schemas import IngestResponse
from app.services.pipeline import run_ingest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/ingest/run", response_model=IngestResponse)
async def ingest_run(db: Session = Depends(get_db)):
    result = await run_ingest(db)
    return result


@router.post("/cleanup/finnhub")
async def cleanup_finnhub(db: Session = Depends(get_db)):
    """
    Finnhub 소스의 모든 기사와 분석 데이터를 삭제합니다.
    """
    # Finnhub 소스 찾기
    finnhub_source = db.query(Source).filter(Source.name == "finnhub").first()

    if not finnhub_source:
        return {"deleted_articles": 0, "deleted_analyses": 0, "message": "Finnhub source not found"}

    # Finnhub 기사들의 ID 수집
    finnhub_article_ids = [
        article.id for article in
        db.query(Article).filter(Article.source_id == finnhub_source.id).all()
    ]

    # 해당 기사들의 분석 데이터 삭제
    deleted_analyses = db.query(Analysis).filter(
        Analysis.article_id.in_(finnhub_article_ids)
    ).delete(synchronize_session=False) if finnhub_article_ids else 0

    # Finnhub 기사 삭제
    deleted_articles = db.query(Article).filter(
        Article.source_id == finnhub_source.id
    ).delete(synchronize_session=False)

    # Finnhub 소스도 삭제 (선택사항)
    db.delete(finnhub_source)

    db.commit()

    return {
        "deleted_articles": deleted_articles,
        "deleted_analyses": deleted_analyses,
        "message": f"Successfully deleted {deleted_articles} Finnhub articles and {deleted_analyses} analyses"
    }

