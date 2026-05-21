"""Configuration for Uday's.Daily[Energy]."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _sender_email() -> str:
    sender = os.getenv("SENDER_EMAIL") or os.getenv("SMTP_USERNAME") or "udaythakran2@gmail.com"
    if "<" in sender and ">" in sender:
        return sender
    return f"{NEWSLETTER_NAME} <{sender}>"


RSS_FEEDS: dict[str, str] = {
    "Reuters Energy": "https://www.reutersagency.com/feed/?best-topics=energy",
    "Reuters Environment": "https://www.reutersagency.com/feed/?best-topics=environment",
    "CleanTechnica": "https://cleantechnica.com/feed/",
    "PV Magazine": "https://www.pv-magazine.com/feed/",
    "Windpower Monthly": "https://www.windpowermonthly.com/rss",
    "IEA News": "https://www.iea.org/news/rss",
    "DOE Energy.gov": "https://www.energy.gov/rss.xml",
    "EIA Today in Energy": "https://www.eia.gov/todayinenergy/rss.php",
}

NEWSLETTER_NAME = "Uday's.Daily[Energy]"

DEFAULT_RECIPIENT_EMAILS: tuple[str, ...] = (
    "udaythakran2@gmail.com",
    "eshasinghthakran@gmail.com",
)

TOPIC_KEYWORDS: tuple[str, ...] = (
    "battery",
    "grid",
    "solar",
    "wind",
    "renewable",
    "hydrogen",
    "nuclear",
    "carbon",
    "storage",
    "transmission",
    "electricity",
    "power",
    "oil",
    "gas",
    "geothermal",
    "ev",
    "climate",
    "energy",
)

ACADEMIC_QUERIES: tuple[str, ...] = (
    'cat:eess.SY AND (energy OR grid OR "power systems" OR storage)',
    'cat:physics.ao-ph AND (climate OR energy OR "renewable energy")',
    'cat:cs.LG AND (energy OR grid OR electricity OR battery)',
)

NEWSAPI_QUERY = (
    '("energy storage" OR solar OR wind OR grid OR hydrogen OR nuclear OR '
    '"power markets" OR "energy policy")'
)

WEB_SEARCH_QUERIES: tuple[str, ...] = (
    "latest energy sector policy renewable grid storage today",
    "energy markets oil gas electricity prices today",
)


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    newsapi_key: str | None = field(default_factory=lambda: os.getenv("NEWSAPI_KEY"))
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_username: str | None = field(default_factory=lambda: os.getenv("SMTP_USERNAME"))
    smtp_password: str | None = field(default_factory=lambda: os.getenv("SMTP_PASSWORD"))
    recipient_emails: tuple[str, ...] = field(
        default_factory=lambda: tuple(_split_csv(os.getenv("RECIPIENT_EMAILS"))) or DEFAULT_RECIPIENT_EMAILS
    )
    sender_email: str = field(default_factory=_sender_email)
    dry_run: bool = field(default_factory=lambda: os.getenv("DRY_RUN", "false").lower() in {"1", "true", "yes"})
    days_back: int = field(default_factory=lambda: int(os.getenv("DAYS_BACK", "2")))
    max_items_per_source: int = field(default_factory=lambda: int(os.getenv("MAX_ITEMS_PER_SOURCE", "12")))


def require_recipients(recipients: Iterable[str]) -> list[str]:
    emails = [email for email in recipients if email]
    if not emails:
        raise RuntimeError("RECIPIENT_EMAILS must contain at least one email address.")
    return emails
