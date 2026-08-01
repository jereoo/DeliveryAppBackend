# Release 1.1.0 — Architecture Refactor (API, semver MINOR)

**Date:** August 1, 2026  
**Heroku app:** `truck-buddy`  
**Health check:** `GET /api/health/` → `"version": "1.1.0"`

**Semver:** `1.0.0` → `1.1.0` — internal architecture improvements and additive `/api/me/`; **no breaking API or database contract changes**. Product scope remains **v1.0** (not commercial multi-tenant v2.0).

> **Note:** Tag `release/2.0.0` was applied briefly but corrected — `2.0.0` implied breaking changes incorrectly.

---

## Revert baseline (checkpoint before this work)

| Repo | Tag | Commit |
|------|-----|--------|
| **DeliveryAppBackend** | `checkpoint/pre-phase-b` | `402e948` — Add GET /api/me/… |
| **DeliveryAppMobile** | `checkpoint/pre-phase-b` | `2038672` — Phase A frontend refactor |

To restore pre–Phase B backend:

```powershell
cd C:\Users\360WEB\DeliveryAppBackend
git fetch origin --tags
git checkout main
git reset --hard checkpoint/pre-phase-b
git push origin main --force   # only if you intentionally roll back production
```

---

## Phase A

- `GET /api/me/` — server-authoritative role (`admin` | `customer` | `driver`)
- Frontend: `authService`, extracted services, screens, theme (mobile repo)

---

## Phase B (backend)

- **`delivery/permissions.py`** — DRF permission classes + queryset scoping helpers
- **ViewSets migrated** — Customer, Delivery, Driver, DriverVehicle, DeliveryAssignment
- **`delivery/registration_service.py`** — customer/driver registration SSOT
- **`DriverVehicleViewSet`** — staff sees all rows; drivers see own; customers see none
- **Tests:** `tests/test_permissions.py`, `tests/test_registration_service.py`

---

## Smoke test after deploy

```powershell
cd C:\Users\360WEB\DeliveryAppBackend
Invoke-RestMethod -Uri "https://truck-buddy-f14f250ae8b3.herokuapp.com/api/health/"
# Expect version 1.1.0 + release_note

$env:ADMIN_USERNAME = "admin"
$env:ADMIN_PASSWORD = "<Heroku ADMIN_PASSWORD>"
.\scripts\production-smoke-test.ps1
```
