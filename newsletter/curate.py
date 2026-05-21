"""Deduplicate, rank, and summarize newsletter content."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from urllib.parse import urlparse

from newsletter.models import DigestSections, Item


SECTION_LIMITS = {
    "top_stories": 4,
    "academic_spotlight": 4,
    "data_markets": 3,
    "policy_pulse": 2,
}

SECTION_TITLES = {
    "top_stories": "Top Stories",
    "academic_spotlight": "Academic Spotlight",
    "data_markets": "Data & Markets",
    "policy_pulse": "Policy Pulse",
}


def _fingerprint(item: Item) -> str:
    host = urlparse(item.url).netloc.lower().replace("www.", "")
    title = re.sub(r"[^a-z0-9 ]", "", item.title.lower())
    words = " ".join(title.split()[:8])
    return f"{host}:{words}"


def dedupe(items: list[Item]) -> list[Item]:
    seen: dict[str, Item] = {}
    for item in items:
        key = _fingerprint(item)
        current = seen.get(key)
        if not current or item.score > current.score or len(item.summary) > len(current.summary):
            seen[key] = item
    return list(seen.values())


def _heuristic_score(item: Item) -> float:
    score = item.score
    title = item.title.lower()
    for keyword, weight in {
        "breakthrough": 8,
        "record": 6,
        "grid": 5,
        "storage": 5,
        "policy": 4,
        "tariff": 4,
        "market": 3,
        "solar": 3,
        "wind": 3,
        "battery": 4,
    }.items():
        if keyword in title:
            score += weight
    if item.published_at:
        score += 3
    if item.section_hint == "academic_spotlight":
        score += 5
    return score


def _trim_summary(text: str, max_words: int = 45) -> str:
    words = re.sub(r"<[^>]+>", "", text).split()
    if not words:
        return ""
    trimmed = " ".join(words[:max_words])
    return trimmed + ("..." if len(words) > max_words else "")


def _fallback_curate(items: list[Item]) -> DigestSections:
    buckets: dict[str, list[Item]] = defaultdict(list)
    for item in dedupe(items):
        section = item.section_hint if item.section_hint in SECTION_LIMITS else "top_stories"
        item.score = _heuristic_score(item)
        item.summary = _trim_summary(item.summary) or "Selected for relevance to energy sector developments today."
        buckets[section].append(item)

    sections: DigestSections = {}
    for section, limit in SECTION_LIMITS.items():
        sections[section] = sorted(buckets.get(section, []), key=lambda row: row.score, reverse=True)[:limit]
    return sections


def _serialize_for_prompt(items: list[Item]) -> list[dict[str, object]]:
    return [
        {
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "summary": item.summary[:1200],
            "section_hint": item.section_hint,
            "authors": item.authors[:6],
            "score": item.score,
            "published_at": item.published_at.isoformat() if item.published_at else None,
        }
        for item in items
    ]


def curate_with_claude(items: list[Item], anthropic_api_key: str | None) -> DigestSections:
    if not anthropic_api_key:
        return _fallback_curate(items)

    try:
        from anthropic import Anthropic
    except ImportError:
        return _fallback_curate(items)

    unique = dedupe(items)
    prompt = f"""
You curate Uday's.Daily[Energy], a daily energy sector newsletter.

Requirements:
- Select 3-4 top stories, 3-4 academic papers, 2-3 data/market items, and 1-2 policy items.
- Academic Spotlight should be roughly half of the selected content.
- Deduplicate overlapping coverage.
- Rank by impact, recency, credibility, and usefulness to an energy-sector reader.
- Rewrite each summary in two concise sentences.
- Return only JSON with keys: top_stories, academic_spotlight, data_markets, policy_pulse.
- Each item must include: title, url, source, summary, authors.

Candidate items:
{json.dumps(_serialize_for_prompt(unique[:120]), ensure_ascii=False)}
""".strip()

    try:
        client = Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=3500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text")
        start = raw.find("{")
        end = raw.rfind("}")
        data = json.loads(raw[start : end + 1])
    except Exception as exc:  # noqa: BLE001 - keep the daily job alive.
        print(f"curation warning: {exc}")
        return _fallback_curate(unique)

    by_url = {item.url: item for item in unique}
    sections: DigestSections = {}
    for section, limit in SECTION_LIMITS.items():
        selected: list[Item] = []
        for row in data.get(section, [])[:limit]:
            base = by_url.get(row.get("url"))
            if base:
                base.summary = row.get("summary") or base.summary
                base.title = row.get("title") or base.title
                base.source = row.get("source") or base.source
                base.authors = row.get("authors") or base.authors
                selected.append(base)
        sections[section] = selected
    return sections
