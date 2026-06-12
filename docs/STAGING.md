# Staging Environment (Optional) — Phase 2

**Status:** Documented — not provisioned by default  
**Production app:** `truck-buddy` (do not seed demo data here)

---

## Purpose

A **second Heroku app** for QA before promoting changes to production:

- Run migrations safely
- Load `seed_demo_data` with known accounts
- Point Vercel **preview** or local mobile at staging API

---

## Recommended setup

| Item | Staging | Production |
|------|---------|------------|
| Heroku app | e.g. `truck-buddy-staging` | `truck-buddy` |
| Postgres | Heroku Postgres (mini) | Heroku Postgres |
| `ALLOW_DEMO_SEED` | `1` | **unset** |
| `ADMIN_PASSWORD` | Staging-only secret | Production secret |
| GitHub deploy | `main` or `staging` branch | `main` |

---

## One-time provisioning (manual)

1. Heroku Dashboard → New app → `truck-buddy-staging`
2. Add Heroku Postgres
3. Connect `DeliveryAppBackend` GitHub repo (Deploy branch: `main` or `staging`)
4. Config vars:
   ```
   SECRET_KEY=<staging-secret>
   DEBUG=False
   ALLOW_DEMO_SEED=1
   ADMIN_PASSWORD=<staging-admin-12+chars>
   CORS_ORIGINS=https://deliveryapp-mobile.vercel.app,http://localhost:19006
   ```
5. Deploy → Run:
   ```bash
   heroku run python manage.py migrate -a truck-buddy-staging
   heroku run python manage.py ensure_admin -a truck-buddy-staging
   heroku run python manage.py seed_demo_data --if-empty -a truck-buddy-staging
   ```

---

## Mobile / frontend

Point API at staging for manual QA:

- Local: `BACKEND_URL` in `.env` or `app.json` extra
- Vercel preview: `EXPO_PUBLIC_BACKEND_URL=https://truck-buddy-staging.herokuapp.com/api`

Do not change production Vercel env unless intentionally switching prod API.

---

## When staging is not needed

Single-app teams can use **local dev + prod smoke** only (`docs/SEED_DATA.md` local seed). Staging is **optional** in PROJECT_PLAN Phase 2.

---

## Related

- [`SEED_DATA.md`](SEED_DATA.md)
- [`ROLLBACK.md`](ROLLBACK.md)
