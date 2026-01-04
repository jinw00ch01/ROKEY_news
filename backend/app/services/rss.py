from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

import feedparser
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


async def fetch_feed(url: str, source_name: str) -> List[NormalizedArticle]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        parsed = feedparser.parse(response.text)

    items: List[NormalizedArticle] = []
    for entry in parsed.entries:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])

        content = ""
        if entry.get("content"):
            content = entry.content[0].value
        elif entry.get("summary"):
            content = entry.summary

        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        items.append(
            NormalizedArticle(
                title=title,
                link=link,
                published_at=published,
                content=content,
                source_name=source_name,
                hash=_compute_hash(link, title),
            )
        )
    return items


async def fetch_multiple(feeds: Iterable[tuple[str, str]]) -> list[NormalizedArticle]:
    collected: list[NormalizedArticle] = []
    for url, name in feeds:
        collected.extend(await fetch_feed(url, name))
    return collected

