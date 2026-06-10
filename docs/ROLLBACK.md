# Rollback guide — production deployments

**Last updated:** June 9, 2026  
**Apps:** Heroku `truck-buddy` (API) · Vercel `deliveryapp-mobile` (web)

Use this when a deploy causes regressions and you need the previous working version live quickly.

---

## Backend — Heroku (`truck-buddy`)

### 1. List recent releases

```bash
heroku releases -a truck-buddy
```

Note the **vNNN** of the last known-good release.

### 2. Roll back to a prior release

```bash
heroku rollback vNNN -a truck-buddy
```

Example: `heroku rollback v42 -a truck-buddy`

This restores the **slug** (compiled app) from that release. It does **not** reverse database migrations automatically. If the bad deploy included migrations, you may need a forward-fix migration or manual DB repair.

### 3. Verify

```powershell
Invoke-RestMethod -Uri "https://truck-buddy-f14f250ae8b3.herokuapp.com/api/health/"
```

Run `scripts/production-smoke-test.ps1` with `ADMIN_PASSWORD` set when possible.

### 4. Re-deploy from Git (alternative)

Heroku Dashboard → **truck-buddy** → **Deploy** → select a previous commit on `main` and deploy manually.

---

## Frontend — Vercel (`deliveryapp-mobile`)

### Option A — Promote a previous deployment (fastest)

1. [Vercel Dashboard](https://vercel.com) → project **deliveryapp-mobile**
2. **Deployments** tab
3. Find the last green deployment before the bad one
4. **⋯** menu → **Promote to Production**

### Option B — Git revert + push

```bash
cd C:\Users\360WEB\DeliveryAppMobile
git revert <bad-commit-sha>
git push origin main
```

Vercel builds and deploys the revert automatically.

---

## Coordinated rollback (API + web)

When a release spans **both** repos (e.g. new API field + mobile UI):

1. Roll back **mobile first** if the UI breaks but the API is backward compatible.
2. Roll back **API** if the backend change breaks existing clients.
3. If both changed in lockstep, roll back both to releases/commits from the same date.

| Service | Last known-good reference (June 9, 2026) |
|---------|------------------------------------------|
| Backend | GitHub `main` @ vehicle lifecycle commits |
| Mobile | GitHub `main` @ vehicle lifecycle UI commits |

Update this table after each verified production release.

---

## Database caution

Heroku Postgres **rollbacks** of data are not part of `heroku rollback`. For schema issues:

- Prefer a **forward-fix** migration on a new release.
- Heroku PG backups: `heroku pg:backups -a truck-buddy` (requires PG add-on plan).

---

## Checklist after rollback

- [ ] `/api/health/` returns OK
- [ ] Vercel web loads (https://deliveryapp-mobile.vercel.app/)
- [ ] Admin login works
- [ ] Driver login + vehicle status display works
- [ ] Note incident in `DeliveryApp/project-docs/PROJECT_STATUS_*.md`
