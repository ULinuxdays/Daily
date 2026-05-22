"""Optional Claude-powered web search gap filler."""

from __future__ import annotations

import json

from newsletter.config import NewsletterProfile, get_profile
from newsletter.models import Item


def fetch_web(
    anthropic_api_key: str | None,
    max_results: int = 6,
    profile: NewsletterProfile | None = None,
) -> list[Item]:
    if not anthropic_api_key:
        return []
    profile = profile or get_profile()

    try:
        from anthropic import Anthropic
    except ImportError:
        return []

    client = Anthropic(api_key=anthropic_api_key)
    if profile.key == "ai":
        section_names = ", ".join(profile.sections)
        prompt = (
            "Find current, high-impact AI developments from the last 48 hours. "
            "Cover governance and government regulation, technical research advances, AI ethics, "
            "existential-risk analysis and management, and business/investment activity. "
            "Return only JSON: an array of objects with title, url, source, summary, section_hint. "
            f"section_hint must be one of: {section_names}. "
            f"Search themes: {', '.join(profile.web_search_queries)}"
        )
    else:
        prompt = (
            "Find current, high-impact energy sector news from the last 48 hours. "
            "Prioritize renewable power, grid, storage, policy, market-moving items, and global business activity. "
            "Include deals and investments: financings, acquisitions, PPAs, project finance, joint ventures, "
            "offtake agreements, and strategic capital allocation across regions. "
            "Return only JSON: an array of objects with title, url, source, summary, section_hint. "
            "Use section_hint='business_deals' for deals, investments, M&A, and project-finance items. "
            f"Search themes: {', '.join(profile.web_search_queries)}"
        )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1200,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}],
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # noqa: BLE001 - optional fallback.
        print(f"web fetch warning: {exc}")
        return []

    text_parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    raw = "\n".join(text_parts).strip()
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        return []

    try:
        rows = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return []

    items: list[Item] = []
    for row in rows[:max_results]:
        title = (row.get("title") or "").strip()
        url = (row.get("url") or "").strip()
        if not title or not url:
            continue
        items.append(
            Item(
                title=title,
                url=url,
                source=(row.get("source") or "Web").strip(),
                summary=(row.get("summary") or "").strip(),
                section_hint=(row.get("section_hint") or "top_stories").strip(),
            )
        )
    return items
