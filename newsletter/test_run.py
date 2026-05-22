"""Local preview runner.

Usage:
    DRY_RUN=true python -m newsletter.test_run
    SAMPLE_DATA=true python -m newsletter.test_run
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from newsletter.curate import curate_with_claude
from newsletter.config import Settings
from newsletter.main import collect_items
from newsletter.render import render_digest
from newsletter.sample_data import sample_items


def main() -> None:
    load_dotenv()
    settings = Settings()
    import os

    items = sample_items(settings.profile) if os.getenv("SAMPLE_DATA", "").lower() in {"1", "true", "yes"} else collect_items(settings)
    sections = curate_with_claude(items, settings.anthropic_api_key, settings.profile)
    html = render_digest(sections, profile=settings.profile)
    path = Path(f"digest-preview-{settings.profile.key}.html")
    path.write_text(html, encoding="utf-8")
    print(f"Fetched {len(items)} candidate items")
    for section, rows in sections.items():
        print(f"{section}: {len(rows)} selected")
    print(f"Preview written to {path.resolve()}")


if __name__ == "__main__":
    main()
