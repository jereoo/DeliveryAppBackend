# CI/CD — DeliveryAppBackend

**Last updated:** July 16, 2026  
**Canonical workflow:** `.github/workflows/phase1-ci.yml`  
**Deploy verify:** `.github/workflows/deploy-verify.yml`  
**Production:** Heroku `truck-buddy` (auto-deploy from `main`)

---

## What runs on push/PR to `main`

| Step | Purpose |
|------|---------|
| Postgres 15 service | Test database |
| `python manage.py migrate` | Apply migrations |
| Critical test suite | Gates merge — must pass |
| Full Django test suite | All tests — must pass |
| `collectstatic --dry-run` | Deploy smoke check |

### Critical tests (must pass)

```
tests.test_api.AuthenticationAPITests
tests.test_api.DriverSelfServiceAPITests
tests.test_api.VehicleLifecycleAPITests
tests.test_driver_vehicle_crud
tests.test_registration_validation
tests.test_auth_logging
tests.test_compliance
tests.test_seed_demo_data
```

Run locally:

```powershell
cd DeliveryAppBackend
python manage.py test tests.test_api.AuthenticationAPITests tests.test_api.DriverSelfServiceAPITests tests.test_api.VehicleLifecycleAPITests tests.test_driver_vehicle_crud tests.test_registration_validation tests.test_auth_logging tests.test_compliance tests.test_seed_demo_data --verbosity=1 --no-input
python manage.py test --verbosity=1 --no-input
```

---

## Retired workflows

| File | Reason |
|------|--------|
| `ci-cd.yml` | Legacy monorepo layout (`DeliveryAppBackend/` subfolder); replaced by `phase1-ci.yml` |

---

## Deploy verification (after CI on `main`)

Workflow **`Verify Heroku Deploy`** runs automatically after **Phase 1 Backend CI** succeeds on a push to `main`. It:

1. Polls Heroku builds until commit `github.sha` is deployed (20 min timeout)
2. Smoke-tests `GET /api/health/` → 200
3. Sets GitHub commit status **`deploy/heroku-production`** (success or failure)
4. **Fails the workflow** if auto-deploy did not happen — visible in GitHub Actions and email (if you watch the repo)
5. Optionally posts to **`DEPLOY_NOTIFY_WEBHOOK_URL`** (Slack/Discord-compatible JSON)

### Required GitHub secret

| Secret | How to get it |
|--------|----------------|
| `HEROKU_API_KEY` | [Heroku Account → Applications → Create authorization](https://dashboard.heroku.com/account/applications/authorizations) |

### Optional GitHub secret

| Secret | Purpose |
|--------|---------|
| `DEPLOY_NOTIFY_WEBHOOK_URL` | Slack/Discord incoming webhook for success + failure messages |

### GitHub email notifications

Profile → **Notifications** → enable **Actions** (workflow failures) for email alerts when deploy verify fails.

---

## Branch strategy

- **`main`** → production (Heroku auto-deploy)
- PRs must pass **Phase 1 Backend CI** before merge

---

## Rollback

See [`docs/ROLLBACK.md`](ROLLBACK.md).

---

## Related

| Repo | Workflow |
|------|----------|
| DeliveryAppMobile | `.github/workflows/phase1-ci.yml` (Expo web build) |
| Both | `docs/DEVELOPMENT_PROCESS.md` in mobile repo |
