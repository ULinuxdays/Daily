"""Configuration for Uday's daily newsletters."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class SectionConfig:
    title: str
    description: str
    limit: int


@dataclass(frozen=True)
class NewsletterProfile:
    key: str
    name: str
    default_recipients: tuple[str, ...]
    rss_feeds: dict[str, str]
    topic_keywords: tuple[str, ...]
    academic_queries: tuple[str, ...]
    semantic_scholar_queries: tuple[str, ...]
    openalex_search: str
    newsapi_query: str
    web_search_queries: tuple[str, ...]
    sections: dict[str, SectionConfig]
    description: str

    @property
    def section_limits(self) -> dict[str, int]:
        return {key: section.limit for key, section in self.sections.items()}

    @property
    def section_titles(self) -> dict[str, str]:
        return {key: section.title for key, section in self.sections.items()}

    @property
    def section_descriptions(self) -> dict[str, str]:
        return {key: section.description for key, section in self.sections.items()}


ENERGY_PROFILE = NewsletterProfile(
    key="energy",
    name="Uday's.Daily[Energy]",
    default_recipients=("eshasinghthakran@gmail.com",),
    rss_feeds={
        "Reuters Energy": "https://www.reutersagency.com/feed/?best-topics=energy",
        "Reuters Environment": "https://www.reutersagency.com/feed/?best-topics=environment",
        "CleanTechnica": "https://cleantechnica.com/feed/",
        "PV Magazine": "https://www.pv-magazine.com/feed/",
        "Windpower Monthly": "https://www.windpowermonthly.com/rss",
        "IEA News": "https://www.iea.org/news/rss",
        "DOE Energy.gov": "https://www.energy.gov/rss.xml",
        "EIA Today in Energy": "https://www.eia.gov/todayinenergy/rss.php",
    },
    topic_keywords=(
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
    ),
    academic_queries=(
        'cat:eess.SY AND (energy OR grid OR "power systems" OR storage)',
        'cat:physics.ao-ph AND (climate OR energy OR "renewable energy")',
        'cat:cs.LG AND (energy OR grid OR electricity OR battery)',
    ),
    semantic_scholar_queries=("energy systems", "power grid optimization", "battery storage renewable energy"),
    openalex_search="energy systems renewable grid storage",
    newsapi_query=(
        '("energy storage" OR solar OR wind OR grid OR hydrogen OR nuclear OR '
        '"power markets" OR "energy policy" OR "energy investment" OR '
        '"renewable energy deal" OR "project finance")'
    ),
    web_search_queries=(
        "latest energy sector policy renewable grid storage today",
        "energy markets oil gas electricity prices today",
        "global energy deals investments acquisitions project finance today",
        "renewable energy battery storage hydrogen investment funding deal today",
    ),
    sections={
        "top_stories": SectionConfig(
            "Top Stories",
            "High-impact developments worth understanding without needing to open the source first.",
            4,
        ),
        "business_deals": SectionConfig(
            "Deals & Investment",
            "Global financings, acquisitions, project investments, PPAs, and strategic capital moves.",
            4,
        ),
        "academic_spotlight": SectionConfig(
            "Academic Spotlight",
            "Research signals, methods, and implications for energy systems, markets, and deployment.",
            4,
        ),
        "data_markets": SectionConfig(
            "Data & Markets",
            "Market, pricing, demand, supply, and infrastructure signals that may affect decisions.",
            3,
        ),
        "policy_pulse": SectionConfig(
            "Policy Pulse",
            "Regulatory and government actions with likely consequences for the sector.",
            2,
        ),
    },
    description=(
        "A self-contained energy-sector briefing: what happened, why it matters, what to watch next, and source links for deeper reading."
    ),
)


AI_PROFILE = NewsletterProfile(
    key="ai",
    name="Uday's.Daily[AI]",
    default_recipients=("udaythakran2@gmail.com", "uday.34.2028@doonschool.com"),
    rss_feeds={
        "OpenAI News": "https://openai.com/news/rss.xml",
        "Google DeepMind Blog": "https://deepmind.google/blog/rss.xml",
        "Anthropic News": "https://www.anthropic.com/news/rss.xml",
        "AI News": "https://artificialintelligence-news.com/feed/",
        "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
        "The Gradient": "https://thegradient.pub/rss/",
        "NIST AI": "https://www.nist.gov/news-events/news/rss.xml",
    },
    topic_keywords=(
        "ai",
        "artificial intelligence",
        "machine learning",
        "model",
        "llm",
        "agent",
        "governance",
        "regulation",
        "policy",
        "safety",
        "alignment",
        "ethics",
        "existential risk",
        "frontier",
        "investment",
        "funding",
        "chip",
        "compute",
    ),
    academic_queries=(
        'cat:cs.AI AND ("artificial intelligence" OR governance OR safety OR alignment)',
        'cat:cs.LG AND ("large language model" OR "foundation model" OR agent OR reasoning)',
        'cat:cs.CY AND ("AI ethics" OR algorithmic OR governance)',
    ),
    semantic_scholar_queries=(
        "AI governance regulation policy",
        "large language models technical advances",
        "AI ethics alignment existential risk",
    ),
    openalex_search="artificial intelligence governance ethics alignment large language models",
    newsapi_query=(
        '("artificial intelligence" OR AI OR "large language model" OR "foundation model" OR '
        '"AI regulation" OR "AI governance" OR "AI safety" OR "AI ethics" OR "AI investment")'
    ),
    web_search_queries=(
        "today AI governance regulation government action policy",
        "today AI technical development research advancement model benchmark",
        "today AI ethics moral philosophy responsible AI development",
        "today AI existential risk safety alignment management work",
        "today AI business investment funding acquisition chips compute",
    ),
    sections={
        "governance": SectionConfig(
            "Governance",
            "Major policy, regulatory, and government actions shaping how AI is governed.",
            5,
        ),
        "technical_development": SectionConfig(
            "Technical Development",
            "New scientific, model, systems, benchmark, and research advances in AI.",
            5,
        ),
        "ai_ethics": SectionConfig(
            "Developments in AI Ethics",
            "Philosophical, moral, social, and responsible-AI questions raised by current AI work.",
            4,
        ),
        "xrisk_management": SectionConfig(
            "Existential Risk Analysis & Management",
            "AI safety, alignment, frontier-risk evaluation, threat modeling, and risk-reduction work.",
            4,
        ),
        "business": SectionConfig(
            "Business",
            "Investment, revenue, infrastructure, chips, acquisitions, partnerships, and market strategy.",
            5,
        ),
    },
    description=(
        "A self-contained AI briefing across governance, technical research, ethics, existential-risk management, and business developments."
    ),
)


NEWSLETTER_PROFILES: dict[str, NewsletterProfile] = {
    ENERGY_PROFILE.key: ENERGY_PROFILE,
    AI_PROFILE.key: AI_PROFILE,
}

# Backward-compatible names for older helper modules and ad hoc commands.
NEWSLETTER_NAME = ENERGY_PROFILE.name
RSS_FEEDS = ENERGY_PROFILE.rss_feeds
TOPIC_KEYWORDS = ENERGY_PROFILE.topic_keywords
ACADEMIC_QUERIES = ENERGY_PROFILE.academic_queries
NEWSAPI_QUERY = ENERGY_PROFILE.newsapi_query
WEB_SEARCH_QUERIES = ENERGY_PROFILE.web_search_queries
DEALS_NEWS_QUERIES = (
    '"renewable energy" investment deal project finance',
    '"energy storage" funding investment acquisition',
    '"solar" "wind" power purchase agreement investment',
    '"green hydrogen" investment deal funding',
    '"oil and gas" acquisition energy deal',
    '"grid" transmission investment financing',
)


def get_profile(key: str | None = None) -> NewsletterProfile:
    normalized = (key or os.getenv("NEWSLETTER_PROFILE") or "energy").strip().lower()
    try:
        return NEWSLETTER_PROFILES[normalized]
    except KeyError as exc:
        choices = ", ".join(sorted(NEWSLETTER_PROFILES))
        raise RuntimeError(f"Unknown NEWSLETTER_PROFILE={normalized!r}. Expected one of: {choices}.") from exc


def _sender_email(profile: NewsletterProfile) -> str:
    sender = os.getenv("SENDER_EMAIL") or os.getenv("SMTP_USERNAME") or "udaythakran2@gmail.com"
    if "<" in sender and ">" in sender:
        return sender
    return f"{profile.name} <{sender}>"


@dataclass
class Settings:
    profile_name: str = field(default_factory=lambda: os.getenv("NEWSLETTER_PROFILE", "energy").lower())
    anthropic_api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    newsapi_key: str | None = field(default_factory=lambda: os.getenv("NEWSAPI_KEY"))
    send_provider: str = field(default_factory=lambda: os.getenv("SEND_PROVIDER", "smtp").lower())
    gog_account: str = field(default_factory=lambda: os.getenv("GOG_ACCOUNT", "udaythakran2@gmail.com"))
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_username: str | None = field(default_factory=lambda: os.getenv("SMTP_USERNAME"))
    smtp_password: str | None = field(default_factory=lambda: os.getenv("SMTP_PASSWORD"))
    recipient_emails: tuple[str, ...] = field(default_factory=tuple)
    sender_email: str = ""
    dry_run: bool = field(default_factory=lambda: os.getenv("DRY_RUN", "false").lower() in {"1", "true", "yes"})
    days_back: int = field(default_factory=lambda: int(os.getenv("DAYS_BACK", "2")))
    max_items_per_source: int = field(default_factory=lambda: int(os.getenv("MAX_ITEMS_PER_SOURCE", "12")))

    def __post_init__(self) -> None:
        self.profile = get_profile(self.profile_name)
        env_recipients = tuple(_split_csv(os.getenv("RECIPIENT_EMAILS")))
        self.recipient_emails = env_recipients or self.profile.default_recipients
        self.sender_email = _sender_email(self.profile)


def require_recipients(recipients: Iterable[str]) -> list[str]:
    emails = [email for email in recipients if email]
    if not emails:
        raise RuntimeError("At least one recipient email address is required.")
    return emails
