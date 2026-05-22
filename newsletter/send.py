"""Email delivery for the newsletter."""

from __future__ import annotations

import smtplib
import base64
import json
import ssl
import subprocess
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from newsletter.config import NewsletterProfile, get_profile, require_recipients


def _subject(profile: NewsletterProfile | None = None) -> str:
    profile = profile or get_profile()
    return f"{profile.name} - {datetime.now().strftime('%b %-d, %Y')}"


def send_with_gog(
    html: str,
    *,
    text_body: str,
    recipients: tuple[str, ...] | list[str],
    account: str,
    profile: NewsletterProfile | None = None,
    dry_run: bool = False,
) -> dict:
    """Send through Gmail SMTP using the refresh token managed by gog."""

    to = require_recipients(recipients)
    profile = profile or get_profile()
    subject = _subject(profile)

    if dry_run:
        return {"dry_run": True, "provider": "gog", "subject": subject, "to": to, "account": account}

    credentials_path = Path.home() / "Library/Application Support/gogcli/credentials.json"
    credentials = json.loads(credentials_path.read_text(encoding="utf-8"))
    try:
        with tempfile.NamedTemporaryFile("r", encoding="utf-8", suffix=".json", delete=False) as handle:
            token_path = Path(handle.name)

        subprocess.run(
            ["gog", "auth", "tokens", "export", account, "--out", str(token_path), "--overwrite", "--no-input"],
            check=True,
            capture_output=True,
            text=True,
        )
        token_data = json.loads(token_path.read_text(encoding="utf-8"))
    finally:
        if "token_path" in locals():
            token_path.unlink(missing_ok=True)

    payload = urllib.parse.urlencode(
        {
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "refresh_token": token_data["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", payload, timeout=30) as response:
        access_token = json.loads(response.read())["access_token"]

    auth = base64.b64encode(f"user={account}\x01auth=Bearer {access_token}\x01\x01".encode()).decode()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        code, response = server.docmd("AUTH", "XOAUTH2 " + auth)
        if code != 235:
            raise RuntimeError(f"Gmail SMTP OAuth failed: {code} {response!r}")

        for recipient in to:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = f"{profile.name} <{account}>"
            message["To"] = recipient
            message["Reply-To"] = account
            message.set_content(text_body)
            message.add_alternative(html, subtype="html")
            server.send_message(message)

    return {
        "sent": True,
        "provider": "gmail-oauth",
        "subject": subject,
        "to": to,
        "account": account,
    }


def send_email(
    html: str,
    *,
    text_body: str,
    recipients: tuple[str, ...] | list[str],
    sender: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str | None,
    smtp_password: str | None,
    profile: NewsletterProfile | None = None,
    dry_run: bool = False,
) -> dict:
    to = require_recipients(recipients)
    subject = _subject(profile)

    if dry_run:
        return {"dry_run": True, "subject": subject, "to": to, "smtp_host": smtp_host}

    if not smtp_username or not smtp_password:
        raise RuntimeError("SMTP_USERNAME and SMTP_PASSWORD are required unless DRY_RUN=true.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(to)
    message.set_content(text_body)
    message.add_alternative(html, subtype="html")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    return {"sent": True, "subject": subject, "to": to, "smtp_host": smtp_host}
