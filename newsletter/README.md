# Uday's.Daily Newsletters

Shared daily newsletter pipeline for:

- `energy` -> `Uday's.Daily[Energy]`
- `ai` -> `Uday's.Daily[AI]`

## Recipients

- Energy: `eshasinghthakran@gmail.com`
- AI: `udaythakran2@gmail.com`, `uday.34.2028@doonschool.com`

Override with `RECIPIENT_EMAILS=a@example.com,b@example.com` if needed.

## Local Preview

Install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r newsletter/requirements.txt
```

Render deterministic sample previews:

```bash
SAMPLE_DATA=true NEWSLETTER_PROFILE=energy .venv/bin/python -m newsletter.test_run
SAMPLE_DATA=true NEWSLETTER_PROFILE=ai .venv/bin/python -m newsletter.test_run
```

Preview files:

- `digest-preview-energy.html`
- `digest-preview-ai.html`

## Local Gmail Delivery

This Mac sends through the locally authorized Google account:

- account: `udaythakran2@gmail.com`
- provider: Gmail SMTP with OAuth tokens managed by `gog`

Send deterministic samples:

```bash
SAMPLE_DATA=true SEND_PROVIDER=gog NEWSLETTER_PROFILE=energy .venv/bin/python -m newsletter.main
SAMPLE_DATA=true SEND_PROVIDER=gog NEWSLETTER_PROFILE=ai .venv/bin/python -m newsletter.main
```

Send live digests:

```bash
SEND_PROVIDER=gog NEWSLETTER_PROFILE=energy .venv/bin/python -m newsletter.main
SEND_PROVIDER=gog NEWSLETTER_PROFILE=ai .venv/bin/python -m newsletter.main
```

## Cloud Schedule

Recurring delivery runs through GitHub Actions, not the laptop. The workflow sends both profiles daily at 7:00 AM India time.

- workflow: `.github/workflows/newsletter.yml`
- cron: `30 1 * * *` UTC
- local time: 7:00 AM Asia/Kolkata
- delivery: SMTP secrets/variables configured in GitHub Actions

Required GitHub Actions secrets:

- `ANTHROPIC_API_KEY`
- `NEWSAPI_KEY`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

Optional GitHub Actions variables:

- `SMTP_HOST` (defaults to `smtp.gmail.com`)
- `SMTP_PORT` (defaults to `587`)
- `SENDER_EMAIL`
