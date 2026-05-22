"""Academic source collection from arXiv, Semantic Scholar, and OpenAlex."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import feedparser
import requests

from newsletter.config import NewsletterProfile, get_profile
from newsletter.models import Item


def _parse_arxiv_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_arxiv(profile: NewsletterProfile | None = None, max_results_per_query: int = 8) -> list[Item]:
    profile = profile or get_profile()
    items: list[Item] = []
    for query in profile.academic_queries:
        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query={quote_plus(query)}&start=0&max_results={max_results_per_query}"
            "&sortBy=submittedDate&sortOrder=descending"
        )
        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "energy-digest/1.0"})
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"arxiv fetch warning ({query}): {exc}")
            continue
        parsed = feedparser.parse(response.content)
        for entry in parsed.entries:
            title = " ".join((entry.get("title") or "").split())
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue
            items.append(
                Item(
                    title=title,
                    url=link,
                    source="arXiv",
                    published_at=_parse_arxiv_time(entry.get("published")),
                    summary=" ".join((entry.get("summary") or "").split()),
                    section_hint="technical_development" if profile.key == "ai" else "academic_spotlight",
                    authors=[author.get("name", "") for author in entry.get("authors", []) if author.get("name")],
                    metadata={"query": query},
                )
            )
    return items


def fetch_semantic_scholar(days_back: int = 7, limit: int = 15, profile: NewsletterProfile | None = None) -> list[Item]:
    profile = profile or get_profile()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    items: list[Item] = []

    for query in profile.semantic_scholar_queries:
        response = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": query,
                "limit": limit,
                "fields": "title,url,abstract,authors,publicationDate,citationCount,openAccessPdf",
                "year": f"{cutoff.year}-",
            },
            timeout=20,
        )
        if response.status_code == 429:
            continue
        response.raise_for_status()
        for paper in response.json().get("data", []):
            title = (paper.get("title") or "").strip()
            url = paper.get("url") or (paper.get("openAccessPdf") or {}).get("url") or ""
            if not title or not url:
                continue
            published_at = None
            if paper.get("publicationDate"):
                try:
                    published_at = datetime.fromisoformat(paper["publicationDate"]).replace(tzinfo=timezone.utc)
                except ValueError:
                    published_at = None
            items.append(
                Item(
                    title=title,
                    url=url,
                    source="Semantic Scholar",
                    published_at=published_at,
                    summary=(paper.get("abstract") or "").strip(),
                    section_hint="technical_development" if profile.key == "ai" else "academic_spotlight",
                    authors=[author.get("name", "") for author in paper.get("authors", []) if author.get("name")],
                    score=float(paper.get("citationCount") or 0),
                    metadata={"query": query, "citation_count": paper.get("citationCount") or 0},
                )
            )
    return items


def fetch_openalex(days_back: int = 7, limit: int = 12, profile: NewsletterProfile | None = None) -> list[Item]:
    profile = profile or get_profile()
    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).date().isoformat()
    response = requests.get(
        "https://api.openalex.org/works",
        params={
            "search": profile.openalex_search,
            "filter": f"from_publication_date:{from_date},is_oa:true",
            "sort": "cited_by_count:desc",
            "per-page": limit,
        },
        timeout=20,
    )
    response.raise_for_status()

    items: list[Item] = []
    for work in response.json().get("results", []):
        title = (work.get("title") or "").strip()
        url = work.get("doi") or work.get("id") or ""
        if url.startswith("https://doi.org/"):
            pass
        elif url.startswith("10."):
            url = f"https://doi.org/{url}"
        if not title or not url:
            continue
        published_at = None
        if work.get("publication_date"):
            try:
                published_at = datetime.fromisoformat(work["publication_date"]).replace(tzinfo=timezone.utc)
            except ValueError:
                published_at = None
        authors = [
            authorship.get("author", {}).get("display_name", "")
            for authorship in work.get("authorships", [])
            if authorship.get("author", {}).get("display_name")
        ]
        items.append(
            Item(
                title=title,
                url=url,
                source="OpenAlex",
                published_at=published_at,
                summary=(work.get("abstract_inverted_index") and "Open-access paper indexed by OpenAlex.") or "",
                section_hint="technical_development" if profile.key == "ai" else "academic_spotlight",
                authors=authors,
                score=float(work.get("cited_by_count") or 0),
                metadata={"citation_count": work.get("cited_by_count") or 0},
            )
        )
    return items


def fetch_academic(days_back: int = 7, profile: NewsletterProfile | None = None) -> list[Item]:
    profile = profile or get_profile()
    items: list[Item] = []
    for fetcher in (
        lambda: fetch_arxiv(profile),
        lambda: fetch_semantic_scholar(days_back, profile=profile),
        lambda: fetch_openalex(days_back, profile=profile),
    ):
        try:
            items.extend(fetcher())
        except Exception as exc:  # noqa: BLE001 - fetchers should fail independently.
            print(f"academic fetch warning: {exc}")
    return items
