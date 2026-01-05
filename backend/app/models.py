from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'finnhub' or 'newsdata'
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    articles: Mapped[list["Article"]] = relationship(back_populates="source")


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (UniqueConstraint("hash", name="uq_articles_hash"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    link: Mapped[str] = mapped_column(String(2048), nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    content_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_clean: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    source: Mapped["Source"] = relationship(back_populates="articles")
    analysis: Mapped[Optional["Analysis"]] = relationship(back_populates="article", uselist=False)


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        UniqueConstraint("article_id", name="uq_analyses_article_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_label: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    keywords: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    json_meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    article: Mapped["Article"] = relationship(back_populates="analysis")
