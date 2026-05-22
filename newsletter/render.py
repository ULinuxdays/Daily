"""Rendering for the newsletter."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from newsletter.config import NewsletterProfile, get_profile
from newsletter.models import DigestSections


TEMPLATE_DIR = Path(__file__).parent / "templates"


def render_digest(
    sections: DigestSections,
    generated_at: datetime | None = None,
    profile: NewsletterProfile | None = None,
) -> str:
    profile = profile or get_profile()
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("digest.html")
    return template.render(
        sections=sections,
        section_descriptions=profile.section_descriptions,
        section_titles=profile.section_titles,
        newsletter_name=profile.name,
        newsletter_description=profile.description,
        generated_at=generated_at or datetime.now(),
    )


def render_text_digest(
    sections: DigestSections,
    generated_at: datetime | None = None,
    profile: NewsletterProfile | None = None,
) -> str:
    profile = profile or get_profile()
    generated = generated_at or datetime.now()
    lines = [
        profile.name,
        generated.strftime("%B %-d, %Y"),
        "",
    ]
    for key, items in sections.items():
        if not items:
            continue
        lines.extend([profile.section_titles[key], profile.section_descriptions.get(key, ""), ""])
        for item in items:
            meta = item.source
            if item.published_label:
                meta += f" - {item.published_label}"
            if item.authors:
                meta += " - " + ", ".join(item.authors[:3])
            lines.extend(
                [
                    item.title,
                    meta,
                    item.summary,
                    f"Source: {item.url}",
                    "",
                ]
            )
    lines.append(f"Sent automatically for {profile.name}. Each item is written to stand alone; links are included for source verification and deeper reading.")
    return "\n".join(lines)
