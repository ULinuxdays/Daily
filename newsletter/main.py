"""Daily Energy Sector Digest entrypoint."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from newsletter.config import Settings
from newsletter.curate import curate_with_claude
from newsletter.fetch.academic import fetch_academic
from newsletter.fetch.newsapi import fetch_newsapi
from newsletter.fetch.rss import fetch_rss
from newsletter.fetch.web import fetch_web
from newsletter.render import render_digest
from newsletter.sample_data import sample_items
from newsletter.send import send_email


def collect_items(settings: Settings) -> list:
    items = []
    for label, fetcher in (
        ("rss", lambda: fetch_rss(settings.days_back, settings.max_items_per_source)),
        ("newsapi", lambda: fetch_newsapi(settings.newsapi_key, settings.days_back)),
        ("academic", lambda: fetch_academic(7)),
        ("web", lambda: fetch_web(settings.anthropic_api_key)),
    ):
        try:
            fetched = fetcher()
            print(f"{label}: {len(fetched)} items")
            items.extend(fetched)
        except Exception as exc:  # noqa: BLE001 - one source should not kill the digest.
            print(f"{label} fetch warning: {exc}")
    return items


def main() -> None:
    load_dotenv()
    settings = Settings()
    import os

    if os.getenv("SAMPLE_DATA", "").lower() in {"1", "true", "yes"}:
        items = sample_items()
        print(f"sample: {len(items)} items")
    else:
        items = collect_items(settings)
    sections = curate_with_claude(items, settings.anthropic_api_key)
    html = render_digest(sections)

    preview_path = Path("digest-preview.html")
    preview_path.write_text(html, encoding="utf-8")
    print(f"wrote preview: {preview_path.resolve()}")

    result = send_email(
        html,
        api_key=settings.resend_api_key,
        recipients=settings.recipient_emails,
        sender=settings.sender_email,
        dry_run=settings.dry_run,
    )
    print(f"send result: {result}")


if __name__ == "__main__":
    main()
