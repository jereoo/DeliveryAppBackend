# Phase 4D — Compliance ops (backend API)

**Status:** Backend API **partial** (July 2026). Mobile admin UI + email reminders still Todo.

---

## Staff API endpoints

All require JWT + `is_staff=True`.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/compliance/admin/summary/` | Fleet counts: pending docs, expired, expiring soon, drivers pending approval |
| GET | `/api/compliance/admin/inbox/` | All `PENDING` legal documents with driver/vehicle context |
| GET | `/api/compliance/admin/expiring/` | Documents expiring within N days (includes expired by default) |

### Query params

**`/summary/`**

- `days` — expiring-soon window (default `30`)

**`/expiring/`**

- `days` — window (default `30`)
- `include_expired=false` — only future expiries within window

### Example summary response

```json
{
  "documents_pending": 3,
  "documents_expired": 1,
  "documents_expiring_soon": 2,
  "drivers_pending_approval": 1,
  "drivers_rejected": 0,
  "expiring_within_days": 30
}
```

---

## Heroku Scheduler (Phase 4B — still manual)

Schedule nightly on **truck-buddy**:

```bash
python manage.py expire_compliance_documents
```

Heroku Dashboard → truck-buddy → **Resources** → add **Heroku Scheduler** → daily job.

---

## Related

- `docs/COMPLIANCE.md` — document types and verify flow
- `docs/SEED_DATA.md` — demo/test accounts for QA
- Mobile Phase 4D UI — Todo (admin inbox screen)
