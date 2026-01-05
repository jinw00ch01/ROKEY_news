from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import httpx


@dataclass
class NormalizedArticle:
    title: str
    link: str
    published_at: Optional[datetime]
    content: str
    source_name: str
    hash: str


def _compute_hash(link: str, title: str) -> str:
    return hashlib.sha256(f"{link}:{title}".encode("utf-8")).hexdigest()


async def fetch_finnhub_news(api_key: str, category: str = "general") -> List[NormalizedArticle]:
    """
    finnhub API를 사용하여 뉴스를 가져옵니다.
    API 문서: https://finnhub.io/docs/api/market-news
    """
    url = "https://finnhub.io/api/v1/news"
    params = {"category": category, "token": api_key}

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    items: List[NormalizedArticle] = []
    for article in data:
        title = article.get("headline", "").strip()
        link = article.get("url", "").strip()
        summary = article.get("summary", "").strip()
        
        if not title or not link:
            continue

        # finnhub timestamp는 Unix timestamp (초)
        published = None
        if article.get("datetime"):
            try:
                published = datetime.fromtimestamp(article["datetime"])
            except (ValueError, OSError):
                pass

        items.append(
            NormalizedArticle(
                title=title,
                link=link,
                published_at=published,
                content=summary,
                source_name=f"finnhub:{category}",
                hash=_compute_hash(link, title),
            )
        )
    return items


async def fetch_newsdata_news(api_key: str, country: str = "kr", language: str = "ko") -> List[NormalizedArticle]:
    """
    NEWSDATA.io API를 사용하여 뉴스를 가져옵니다.
    API 문서: https://newsdata.io/documentation
    """
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": api_key,
        "country": country,
        "language": language,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    items: List[NormalizedArticle] = []
    results = data.get("results", [])
    
    for article in results:
        title = article.get("title", "").strip()
        link = article.get("link", "").strip()
        content = article.get("description", "") or article.get("content", "") or ""
        
        if not title or not link:
            continue

        # NEWSDATA.io pubDate는 ISO 8601 형식
        published = None
        if article.get("pubDate"):
            try:
                # ISO 8601 파싱 (예: "2026-01-05 12:34:56")
                published = datetime.fromisoformat(article["pubDate"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        source_name = article.get("source_id", "newsdata")
        
        items.append(
            NormalizedArticle(
                title=title,
                link=link,
                published_at=published,
                content=content.strip(),
                source_name=f"newsdata:{source_name}",
                hash=_compute_hash(link, title),
            )
        )
    return items


async def fetch_all_news(finnhub_key: Optional[str], newsdata_key: Optional[str]) -> List[NormalizedArticle]:
    """
    finnhub와 NEWSDATA.io API를 모두 호출하여 뉴스를 수집합니다.
    """
    items: List[NormalizedArticle] = []
    
    if finnhub_key:
        try:
            finnhub_items = await fetch_finnhub_news(finnhub_key, category="general")
            items.extend(finnhub_items)
        except Exception as e:
            print(f"Failed to fetch from finnhub: {e}")
    
    if newsdata_key:
        try:
            newsdata_items = await fetch_newsdata_news(newsdata_key, country="kr", language="ko")
            items.extend(newsdata_items)
        except Exception as e:
            print(f"Failed to fetch from NEWSDATA.io: {e}")
    
    return items
