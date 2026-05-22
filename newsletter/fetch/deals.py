"""Business, deals, and investment source collection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

import feedparser
import requests

from newsletter.config import DEALS_NEWS_QUERIES
from newsletter.models import Item


BUSINESS_KEYWORDS = {
    "acquisition",
    "acquires",
    "deal",
    "debt",
    "equity",
    "financing",
    "fund",
    "funding",
    "investment",
    "invests",
    "joint venture",
    "merger",
    "ppa",
    "power purchase",
    "project finance",
    "raises",
    "stake",
}


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if not parsed.tzinfo:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _score(title: str, summary: str) -> float:
    text = f"{title} {summary}".lower()
    score = 8.0
    for keyword in BUSINESS_KEYWORDS:
        if keyword in text:
            score += 4
    for region in ("india", "china", "europe", "africa", "middle east", "latin america", "global"):
        if region in text:
            score += 2
    return score


def fetch_deals(days_back: int = 3, max_results_per_query: int = 8) -> list[Item]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    items: list[Item] = []

    for query in DEALS_NEWS_QUERIES:
        url = (
            "https://news.google.com/rss/search"
            f"?q={quote_plus(query + ' when:7d')}&hl=en-US&gl=US&ceid=US:en"
        )
        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "energy-digest/1.0"})
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"deals fetch warning ({query}): {exc}")
            continue

        parsed = feedparser.parse(response.content)
        for entry in parsed.entries[:max_results_per_query]:
            title = " ".join((entry.get("title") or "").split())
            link = (entry.get("link") or "").strip()
            published_at = _parse_date(entry.get("published"))
            if published_at and published_at < cutoff:
                continue
            if not title or not link:
                continue

            summary = " ".join((entry.get("summary") or "").split())
            items.append(
                Item(
                    title=title,
                    url=link,
                    source="Google News - Deals",
                    published_at=published_at,
                    summary=summary,
                    section_hint="business_deals",
                    score=_score(title, summary),
                    metadata={"query": query},
                )
            )
    return items
