"""RSS feed collection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests

from newsletter.config import NewsletterProfile, get_profile
from newsletter.models import Item


def _parse_date(entry: dict) -> datetime | None:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if not value:
            continue
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except (TypeError, ValueError):
            continue
    return None


def _section_for(profile: NewsletterProfile, source: str, text: str) -> str:
    lower = f"{source} {text}".lower()
    if profile.key == "ai":
        if any(term in lower for term in ("regulation", "regulator", "government", "policy", "law", "nist", "eu ai act", "white house", "senate")):
            return "governance"
        if any(term in lower for term in ("ethic", "bias", "fairness", "responsible", "moral", "philosophy", "rights")):
            return "ai_ethics"
        if any(term in lower for term in ("existential", "x-risk", "xrisk", "safety", "alignment", "frontier risk", "eval", "biosecurity", "catastrophic")):
            return "xrisk_management"
        if any(term in lower for term in ("funding", "investment", "invests", "acquisition", "revenue", "valuation", "startup", "chip", "compute", "data center")):
            return "business"
        return "technical_development"
    if any(term in lower for term in ("eia", "commodity", "market", "prices", "oil", "gas", "lng")):
        return "data_markets"
    if any(term in lower for term in ("policy", "regulation", "doe", "iea", "tax credit", "permitting")):
        return "policy_pulse"
    return "top_stories"


def fetch_rss(days_back: int = 2, max_items_per_source: int = 12, profile: NewsletterProfile | None = None) -> list[Item]:
    profile = profile or get_profile()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    items: list[Item] = []

    for source, url in profile.rss_feeds.items():
        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "energy-digest/1.0"})
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"rss fetch warning ({source}): {exc}")
            continue
        parsed = feedparser.parse(response.content)
        for entry in parsed.entries[:max_items_per_source]:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue

            published_at = _parse_date(entry)
            if published_at and published_at < cutoff:
                continue

            summary = (entry.get("summary") or entry.get("description") or "").strip()
            searchable = f"{title} {summary}".lower()
            if not any(keyword in searchable for keyword in profile.topic_keywords):
                continue

            items.append(
                Item(
                    title=title,
                    url=link,
                    source=source,
                    published_at=published_at,
                    summary=summary,
                    section_hint=_section_for(profile, source, searchable),
                )
            )

    return items
