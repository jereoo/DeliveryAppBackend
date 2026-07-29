# Phase 4D — Compliance ops (backend API + scheduled jobs)

**Status:** Backend API **Done**. Mobile admin UI **Done**. Nightly jobs + email reminders **Done** (deploy + Heroku Scheduler setup required).

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

### Single command (recommended for Heroku Scheduler)

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

## Heroku Scheduler setup (truck-buddy)

### 1. Deploy backend + migrate

After merge to `main` (auto-deploy) or manual deploy:

```bash
heroku run python manage.py migrate -a truck-buddy
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

### 3. Add Heroku Scheduler

Dashboard → **truck-buddy** → **Resources** → **Find more add-ons** → **Heroku Scheduler** → Install (free tier).

### 4. Create daily job

Dashboard → **Heroku Scheduler** → **Add job**:

| Field | Value |
|-------|--------|
| Schedule | Daily (e.g. **06:00 UTC**) |
| Command | `python manage.py run_compliance_daily_jobs` |
| Dyno size | Standard-1X (or Basic if available) |

### 5. Verify (manual one-off)

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
