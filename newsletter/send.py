"""Email delivery through SMTP."""

from __future__ import annotations

import smtplib
from datetime import datetime
from email.message import EmailMessage

from newsletter.config import NEWSLETTER_NAME, require_recipients


def send_email(
    html: str,
    *,
    recipients: tuple[str, ...] | list[str],
    sender: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str | None,
    smtp_password: str | None,
    dry_run: bool = False,
) -> dict:
    to = require_recipients(recipients)
    subject = f"{NEWSLETTER_NAME} - {datetime.now().strftime('%b %-d, %Y')}"

    if dry_run:
        return {"dry_run": True, "subject": subject, "to": to, "smtp_host": smtp_host}

    if not smtp_username or not smtp_password:
        raise RuntimeError("SMTP_USERNAME and SMTP_PASSWORD are required unless DRY_RUN=true.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(to)
    message.set_content("This newsletter is best viewed as HTML.")
    message.add_alternative(html, subtype="html")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    return {"sent": True, "subject": subject, "to": to, "smtp_host": smtp_host}
