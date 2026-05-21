"""NewsAPI fallback collection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from newsletter.config import NEWSAPI_QUERY
from newsletter.models import Item


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_newsapi(api_key: str | None, days_back: int = 2, page_size: int = 30) -> list[Item]:
    if not api_key:
        return []

    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).date().isoformat()
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": NEWSAPI_QUERY,
            "from": from_date,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": api_key,
        },
        timeout=20,
    )
    response.raise_for_status()

    items: list[Item] = []
    for article in response.json().get("articles", []):
        title = (article.get("title") or "").strip()
        url = (article.get("url") or "").strip()
        if not title or not url:
            continue
        source = article.get("source", {}).get("name") or "NewsAPI"
        items.append(
            Item(
                title=title,
                url=url,
                source=source,
                published_at=_parse_iso(article.get("publishedAt")),
                summary=(article.get("description") or "").strip(),
                section_hint="top_stories",
            )
        )
    return items

