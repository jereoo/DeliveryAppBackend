# Phase 4D — Compliance ops (backend API + scheduled jobs)

**Status:** Backend API **Done**. Mobile admin UI **Done**. Nightly jobs + email reminders **Done**. GitHub Actions cron + SMTP on Heroku **ops setup**.

---

## Staff API endpoints

All require JWT + `is_staff=True`.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/compliance/admin/summary/` | Fleet counts: pending docs, expired, expiring soon, drivers pending approval |
| GET | `/api/compliance/admin/inbox/` | All `PENDING` legal documents with driver/vehicle context |
| GET | `/api/compliance/admin/expiring/` | Documents expiring within N days (includes expired by default) |

---

## Nightly jobs (Phase 4D #1 + #2)

### Scheduled via GitHub Actions (recommended)

Workflow **`.github/workflows/compliance-daily-jobs.yml`** runs daily at **06:00 UTC** and starts a Heroku one-off dyno:

```bash
python manage.py run_compliance_daily_jobs
```

Requires GitHub secret **`HEROKU_API_KEY`** (same token as deploy verify).

The workflow starts a one-off `run` dyno and polls **`GET /apps/truck-buddy/dynos`** (list), matching by dyno **name** (`run.N`). One-off dynos disappear from the list when done — that is treated as success.

Manual run: GitHub → **Actions** → **Compliance Daily Jobs** → **Run workflow** (optional `--dry-run`).

### Single command (Heroku one-off / local)

```bash
python manage.py run_compliance_daily_jobs
```

Runs in order:

1. **`expire_compliance_documents`** — marks `VERIFIED` docs with `expiry_date < today` as `EXPIRED`
2. **`send_compliance_expiry_reminders`** — emails drivers at **30**, **14**, and **0** days before expiry (once per threshold per document)

### Individual commands

```bash
python manage.py expire_compliance_documents
python manage.py send_compliance_expiry_reminders
python manage.py run_compliance_daily_jobs --dry-run
```

---

## Ops checklist (truck-buddy)

### 1. Deploy backend + migrate

Migrations run automatically on deploy via `Procfile` release phase:

```procfile
release: python manage.py migrate --noinput
```

### 2. Configure email (required for reminders to send)

Without SMTP config, Django uses the **console** backend — reminders are logged only, not emailed.

**SendGrid (common on Heroku):**

```bash
heroku config:set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend -a truck-buddy
heroku config:set EMAIL_HOST=smtp.sendgrid.net -a truck-buddy
heroku config:set EMAIL_HOST_USER=apikey -a truck-buddy
heroku config:set EMAIL_HOST_PASSWORD=YOUR_SENDGRID_API_KEY -a truck-buddy
heroku config:set EMAIL_USE_TLS=True -a truck-buddy
heroku config:set DEFAULT_FROM_EMAIL=you@yourdomain.com -a truck-buddy
```

Or add the **SendGrid** Heroku add-on and map its credentials to the vars above.

### 3. Enable GitHub cron schedule

1. Ensure **`HEROKU_API_KEY`** is set in GitHub → **DeliveryAppBackend** → Settings → Secrets → Actions (same token as deploy verify).
2. Workflow **`Compliance Daily Jobs`** runs on schedule; confirm under **Actions** after the first 06:00 UTC run.
3. Optional test: **Actions** → **Compliance Daily Jobs** → **Run workflow** → dry-run `true`.

### 4. Verify manually (optional)

```bash
heroku run python manage.py run_compliance_daily_jobs --dry-run -a truck-buddy
heroku run python manage.py run_compliance_daily_jobs -a truck-buddy
```

Check logs:

```bash
heroku logs --tail -a truck-buddy
```

---

## Email reminder behaviour

| Days before expiry | Subject pattern | Sent once |
|--------------------|-----------------|-----------|
| 30 | `Reminder: … expires in 30 days` | `expiry_reminder_30_sent_at` |
| 14 | `Reminder: … expires in 14 days` | `expiry_reminder_14_sent_at` |
| 0 | `Action required: … expires today` | `expiry_reminder_0_sent_at` |

- Recipient: assigned driver's `user.email`
- Only **VERIFIED** documents with `expiry_date` set
- Reminder fields reset when admin **re-verifies** a document

---

## Related

- `docs/COMPLIANCE.md` — document types and verify flow
- `docs/SEED_DATA.md` — demo/test accounts for QA
- Mobile Phase 4D UI — `AdminComplianceScreen` + dashboard summary counts
