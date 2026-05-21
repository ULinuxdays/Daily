"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Item:
    title: str
    url: str
    source: str
    published_at: datetime | None = None
    summary: str = ""
    section_hint: str = "top_stories"
    authors: list[str] = field(default_factory=list)
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def published_label(self) -> str:
        if not self.published_at:
            return ""
        return self.published_at.astimezone(timezone.utc).strftime("%b %-d, %Y")


DigestSections = dict[str, list[Item]]

