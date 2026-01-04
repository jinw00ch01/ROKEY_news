from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis
from app.schemas import AnalysisOut

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    ana = db.query(Analysis).filter(Analysis.id == analysis_id).one_or_none()
    if not ana:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return ana

