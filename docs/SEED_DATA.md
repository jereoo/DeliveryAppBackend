# Seed & Demo Data — Phase 2

**Last updated:** June 12, 2026  
**Applies to:** Local dev, CI, **staging only** — not production `truck-buddy`

---

## Strategy

| Environment | Seed approach |
|-------------|----------------|
| **Local dev** | `seed_demo_data` (small known accounts) or `create_test_data` (bulk) |
| **CI** | Migrations only; tests create their own fixtures |
| **Staging Heroku** | `seed_demo_data --if-empty` after first deploy + `ensure_admin` |
| **Production** | **Never** run bulk seeds; `ensure_admin` only; real users via registration |

---

## Canonical command: `seed_demo_data`

Idempotent demo dataset for QA and staging smoke tests.

```powershell
cd DeliveryAppBackend
python manage.py seed_demo_data
python manage.py seed_demo_data --force      # replace demo.* rows only
python manage.py seed_demo_data --if-empty   # skip if any drivers exist
```

### Demo accounts (staging / local only)

| Role | Username | Password | Notes |
|------|----------|----------|--------|
| Driver | `demo.driver` | `DemoPass1234!` | Approved; Ford F-150 (`DEMO001`); CA-ON license; verified compliance docs |
| Customer | `demo.customer` | `DemoPass1234!` | One pending delivery |
| Admin | `admin` (or `ADMIN_USERNAME`) | `ADMIN_PASSWORD` env | Use `ensure_admin` |

**Do not use these passwords on production.**

Implementation: `delivery/seed_demo.py` + shared helpers in `delivery/seed_helpers.py` → `management/commands/seed_demo_data.py`.

---

## Driver / vehicle CRUD test data: `seed_driver_vehicle_test_data`

Replaces **all** drivers, vehicles, driver assignments, and legal documents with catalog-compliant profiles.  
Does **not** delete customers, deliveries, or delivery assignments.

```powershell
cd DeliveryAppBackend
python manage.py seed_driver_vehicle_test_data --force
```

### Test driver accounts (local / staging only)

| Username | Password | Approval | Active | Legal docs |
|----------|----------|----------|--------|------------|
| `test.driver.approved` | `TestPass1234!` | APPROVED | yes | All verified (license + registration + insurance) |
| `test.driver.pending` | `TestPass1234!` | PENDING | no | All pending |
| `test.driver.rejected` | `TestPass1234!` | REJECTED | no | None |
| `test.driver.partial` | `TestPass1234!` | APPROVED | yes | Verified driver license only; vehicle docs pending |
| `test.driver.inactive` | `TestPass1234!` | APPROVED | no | All verified (inactive vehicle/driver for reactivation QA) |

Vehicles use **`VehicleModelSpec`** catalog entries (Ford F-150, Chevy Silverado 1500, etc.) with valid `license_issuing_region` values.

Implementation: `delivery/seed_driver_vehicle_test_data.py` → `management/commands/seed_driver_vehicle_test_data.py`.

---

## Other commands

| Command | Use case |
|---------|----------|
| `python manage.py ensure_admin` | Bootstrap staff user (all environments) |
| `python manage.py seed_driver_vehicle_test_data --force` | **Driver/vehicle CRUD QA** — replaces all driver/vehicle/legal-doc rows |
| `python manage.py create_test_data --customers 20 --drivers 5` | Bulk load for mobile list testing (**legacy driver fields — prefer seed above**) |
| `python manage.py load_test_data` | **Legacy — broken** (old `Driver.name` model). Do not use. |

---

## Production safety

- `seed_demo_data` **refuses Heroku** unless `ALLOW_DEMO_SEED=1`
- Never set `ALLOW_DEMO_SEED=1` on production app `truck-buddy`
- Staging app only (see `STAGING.md`)

---

## After seeding

1. Login mobile/web as `demo.driver` and `demo.customer`
2. Admin: verify driver, vehicle, customer, delivery in lists
3. Run regression: `python -m pytest tests/test_driver_vehicle_crud.py -v`

---

## Related

- [`STAGING.md`](STAGING.md) — optional staging Heroku app
- [`ADMIN_BOOTSTRAP.md`](ADMIN_BOOTSTRAP.md) — admin user
- Mobile: `docs/DEVELOPMENT_PROCESS.md` — test gates
