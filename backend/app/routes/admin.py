from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IngestResponse
from app.services.pipeline import run_ingest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/ingest/run", response_model=IngestResponse)
async def ingest_run(db: Session = Depends(get_db)):
    result = await run_ingest(db)
    return result

