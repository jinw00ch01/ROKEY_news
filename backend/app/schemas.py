from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class SourceOut(BaseModel):
    id: int
    name: str
    url: str
    active: bool
    last_fetched_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticleOut(BaseModel):
    id: int
    source_id: int
    title: str
    link: str
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    keywords: Optional[list[str]] = None

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    id: int
    article_id: int
    summary: str
    sentiment_label: str
    sentiment_score: float
    keywords: Optional[list[str]] = None
    json_meta: Optional[dict] = None
    model_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ArticlePayload(BaseModel):
    title: str
    content: str
    published_at: Optional[str] = None
    source: Optional[str] = None


class AnalyzeRequest(BaseModel):
    article: ArticlePayload
    need_keywords: bool = True


class SentimentResult(BaseModel):
    label: str = Field(description="positive|neutral|negative")
    score: float = Field(ge=-1.0, le=1.0)


class AnalysisResult(BaseModel):
    summary: str
    sentiment: SentimentResult
    keywords: list[str] = Field(default_factory=list)
    reason: str
    safety_flag: bool = False
    safety_reason: str = ""

