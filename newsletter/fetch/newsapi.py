"""NewsAPI fallback collection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from newsletter.config import NewsletterProfile, get_profile
from newsletter.models import Item


BUSINESS_TERMS = (
    "acquisition",
    "deal",
    "financing",
    "funding",
    "investment",
    "invests",
    "joint venture",
    "merger",
    "power purchase",
    "project finance",
    "raises",
    "stake",
)

GOVERNANCE_TERMS = ("regulation", "regulator", "government", "policy", "law", "bill", "executive order", "nist")
ETHICS_TERMS = ("ethic", "bias", "fairness", "responsible ai", "copyright", "rights", "moral")
XRISK_TERMS = ("existential", "x-risk", "xrisk", "ai safety", "alignment", "frontier risk", "catastrophic", "eval")
TECH_TERMS = ("model", "benchmark", "agent", "reasoning", "training", "inference", "research", "open source")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _ai_section(text: str) -> str:
    if any(term in text for term in GOVERNANCE_TERMS):
        return "governance"
    if any(term in text for term in XRISK_TERMS):
        return "xrisk_management"
    if any(term in text for term in ETHICS_TERMS):
        return "ai_ethics"
    if any(term in text for term in BUSINESS_TERMS) or any(term in text for term in ("funding", "startup", "chip", "compute", "valuation")):
        return "business"
    if any(term in text for term in TECH_TERMS):
        return "technical_development"
    return "technical_development"


def fetch_newsapi(
    api_key: str | None,
    days_back: int = 2,
    page_size: int = 30,
    profile: NewsletterProfile | None = None,
) -> list[Item]:
    if not api_key:
        return []
    profile = profile or get_profile()

    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).date().isoformat()
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": profile.newsapi_query,
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
        text = f"{title} {article.get('description') or ''}".lower()
        if profile.key == "ai":
            section_hint = _ai_section(text)
        else:
            section_hint = "business_deals" if any(term in text for term in BUSINESS_TERMS) else "top_stories"
        items.append(
            Item(
                title=title,
                url=url,
                source=source,
                published_at=_parse_iso(article.get("publishedAt")),
                summary=(article.get("description") or "").strip(),
                section_hint=section_hint,
            )
        )
    return items
