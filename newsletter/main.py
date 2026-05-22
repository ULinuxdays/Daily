"""Daily newsletter entrypoint."""

from __future__ import annotations

import os
import signal
from pathlib import Path

from dotenv import load_dotenv

from newsletter.config import Settings
from newsletter.curate import curate_with_claude
from newsletter.fetch.academic import fetch_academic
from newsletter.fetch.deals import fetch_deals
from newsletter.fetch.newsapi import fetch_newsapi
from newsletter.fetch.rss import fetch_rss
from newsletter.fetch.web import fetch_web
from newsletter.render import render_digest, render_text_digest
from newsletter.sample_data import sample_items
from newsletter.send import send_email, send_with_gog


class FetchTimeoutError(TimeoutError):
    pass


def _timeout_handler(signum, frame):  # noqa: ARG001
    raise FetchTimeoutError("source timed out")


def _call_with_timeout(fetcher, seconds: int):
    previous_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)
    try:
        return fetcher()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


def collect_items(settings: Settings) -> list:
    items = []
    fetch_timeout = int(os.getenv("FETCH_TIMEOUT_SECONDS", "45"))
    fetchers = [
        ("rss", lambda: fetch_rss(settings.days_back, settings.max_items_per_source, settings.profile)),
        ("newsapi", lambda: fetch_newsapi(settings.newsapi_key, settings.days_back, profile=settings.profile)),
        ("academic", lambda: fetch_academic(7, settings.profile)),
        ("web", lambda: fetch_web(settings.anthropic_api_key, profile=settings.profile)),
    ]
    if settings.profile.key == "energy":
        fetchers.insert(2, ("deals", lambda: fetch_deals(settings.days_back, settings.max_items_per_source)))
    for label, fetcher in fetchers:
        try:
            fetched = _call_with_timeout(fetcher, fetch_timeout)
            print(f"{label}: {len(fetched)} items")
            items.extend(fetched)
        except Exception as exc:  # noqa: BLE001 - one source should not kill the digest.
            print(f"{label} fetch warning: {exc}")
    return items


def main() -> None:
    load_dotenv()
    settings = Settings()

    if os.getenv("SAMPLE_DATA", "").lower() in {"1", "true", "yes"}:
        items = sample_items(settings.profile)
        print(f"sample: {len(items)} items")
    else:
        items = collect_items(settings)
    sections = curate_with_claude(items, settings.anthropic_api_key, settings.profile)
    html = render_digest(sections, profile=settings.profile)
    text_body = render_text_digest(sections, profile=settings.profile)

    preview_path = Path(f"digest-preview-{settings.profile.key}.html")
    preview_path.write_text(html, encoding="utf-8")
    print(f"wrote preview: {preview_path.resolve()}")

    if settings.send_provider == "gog":
        result = send_with_gog(
            html,
            text_body=text_body,
            recipients=settings.recipient_emails,
            account=settings.gog_account,
            profile=settings.profile,
            dry_run=settings.dry_run,
        )
    else:
        result = send_email(
            html,
            text_body=text_body,
            recipients=settings.recipient_emails,
            sender=settings.sender_email,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_username=settings.smtp_username,
            smtp_password=settings.smtp_password,
            profile=settings.profile,
            dry_run=settings.dry_run,
        )
    print(f"send result: {result}")


if __name__ == "__main__":
    main()
