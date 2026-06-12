# CI/CD — DeliveryAppBackend

**Last updated:** June 3, 2026  
**Canonical workflow:** `.github/workflows/phase1-ci.yml`  
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
