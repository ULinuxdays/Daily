# Uday's.Daily[Energy]

Daily email newsletter pipeline for energy news, academic papers, markets, and policy.

## Local Preview

Install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r newsletter/requirements.txt
```

Render a deterministic sample preview:

```bash
SAMPLE_DATA=true .venv/bin/python -m newsletter.test_run
```

Render with live fetchers:

```bash
DRY_RUN=true .venv/bin/python -m newsletter.test_run
```

The preview is written to `digest-preview.html`.

## GitHub Secrets

Set these repository secrets:

- `ANTHROPIC_API_KEY`
- `RESEND_API_KEY`
- `NEWSAPI_KEY`

The default sender is `udaythakran2@gmail.com`, formatted as `Uday's.Daily[Energy] <udaythakran2@gmail.com>`. Resend requires this sender address to be verified before real sends will work.

The default recipients are:

- `udaythakran2@gmail.com`
- `eshasinghthakran@gmail.com`

## Schedule

Recurring delivery is intentionally commented out in `.github/workflows/newsletter.yml` until the manual sample send is approved.

To send one sample from GitHub Actions:

- Add the GitHub secrets and `SENDER_EMAIL` repository variable.
- Open Actions -> `Uday's.Daily[Energy]` -> Run workflow.
- Set `sample_data=true` and `send_email=true`.

To preview without sending, run the same workflow with `send_email=false`; it will render `digest-preview.html` in the runner and stop before Resend.

To enable recurring delivery after the sample is approved, uncomment the `schedule` block in `.github/workflows/newsletter.yml`. The workflow runs at both 11:00 and 12:00 UTC, then checks `America/New_York` locally and only sends when the local hour is 7. This keeps the digest at 7am ET across daylight saving changes.
