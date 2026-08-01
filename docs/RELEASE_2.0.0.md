# Release 2.0.0 — Architecture Refactor (API)

**Date:** August 1, 2026  
**Heroku app:** `truck-buddy`  
**Health check:** `GET /api/health/` → `"version": "2.0.0"`

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

## Phase A (already deployed before 2.0.0)

- `GET /api/me/` — server-authoritative role (`admin` | `customer` | `driver`)
- Frontend: `authService`, extracted services, screens, theme (mobile repo)

---

## Phase B (this release — backend)

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
# Expect version 2.0.0 + release_note

$env:ADMIN_USERNAME = "admin"
$env:ADMIN_PASSWORD = "<Heroku ADMIN_PASSWORD>"
.\scripts\production-smoke-test.ps1
```

---

## Product scope unchanged

Still **v1.0 product** (single fleet, admin/driver/customer). Version **2.0.0** marks **API/architecture** maturity, not commercial multi-tenant v2.0.
