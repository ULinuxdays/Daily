"""HTML rendering for the newsletter."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from newsletter.config import NEWSLETTER_NAME
from newsletter.curate import SECTION_TITLES
from newsletter.models import DigestSections


TEMPLATE_DIR = Path(__file__).parent / "templates"


def render_digest(sections: DigestSections, generated_at: datetime | None = None) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("digest.html")
    return template.render(
        sections=sections,
        section_titles=SECTION_TITLES,
        newsletter_name=NEWSLETTER_NAME,
        generated_at=generated_at or datetime.now(),
    )
