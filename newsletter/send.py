"""Email delivery through Resend."""

from __future__ import annotations

from datetime import datetime

import resend

from newsletter.config import NEWSLETTER_NAME, require_recipients


def send_email(
    html: str,
    *,
    api_key: str | None,
    recipients: tuple[str, ...] | list[str],
    sender: str,
    dry_run: bool = False,
) -> dict:
    to = require_recipients(recipients)
    subject = f"{NEWSLETTER_NAME} - {datetime.now().strftime('%b %-d, %Y')}"

    if dry_run:
        return {"dry_run": True, "subject": subject, "to": to}

    if not api_key:
        raise RuntimeError("RESEND_API_KEY is required unless DRY_RUN=true.")
    if "digest@example.com" in sender:
        raise RuntimeError("Set SENDER_EMAIL to a Resend-verified sender before sending.")

    resend.api_key = api_key
    return resend.Emails.send(
        {
            "from": sender,
            "to": to,
            "subject": subject,
            "html": html,
        }
    )
