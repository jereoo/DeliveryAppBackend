# Vehicle lifecycle (v1.0)

Explicit operations for driver-owned vehicles. Avoid generic “edit vehicle” — use **onboard**, **replace**, **comply**, **approve**, and **request resubmit**.

## Approval statuses

| Status | Meaning |
|--------|---------|
| `PENDING` | Driver submitted; inactive until staff approves |
| `APPROVED` | Staff verified identity; driver may operate when compliance docs are verified |
| `RESUBMIT` | Staff found an error; driver must fix and resubmit → becomes `PENDING` |
| `REJECTED` | Staff rejected registration (terminal for that vehicle row) |

## Immutability tiers

1. **Driver + APPROVED** — identity locked; driver may only set `active=false` (mark inactive).
2. **Staff + APPROVED** — identity locked; staff uses **request resubmit** (not PATCH identity).
3. **Driver + RESUBMIT or PENDING** — driver may update identity fields (catalog-backed).
4. **Verified registration doc** — `vin` and `license_plate` locked for driver even in RESUBMIT/PENDING.

## Operations

### Onboard (registration)

`POST /api/drivers/register/` creates vehicle via `vehicle_onboarding_service.create_vehicle_from_catalog()`:

- `approval_status=PENDING`, `active=False`
- Driver uploads compliance while waiting for approval

### Replace (atomic)

`POST /api/drivers/me/vehicles/` — `vehicle_replace_service.replace_driver_vehicle()` in one transaction:

- Closes current assignment; deactivates previous vehicle
- Creates new vehicle `PENDING`, `active=False`
- New vehicle starts with **fresh** compliance docs; old vehicle docs preserved on old row
- Driver **cannot** self-assign as `APPROVED`; new truck is not dispatch-eligible until staff approves

### Resubmit (driver)

After staff `POST /api/vehicles/{id}/resubmit/` with `resubmit_reason`:

- Driver fixes data via `POST /api/drivers/me/vehicle/resubmit/`
- Status → `PENDING`, vehicle inactive until approved again

### Approve (staff)

`POST /api/vehicles/{id}/approve/` — sets `APPROVED`, `active=True` (if compliance allows activation policy elsewhere).

### Current vs history

- `get_current_vehicle(driver)` — open assignment only (`assigned_to IS NULL`)
- `get_driver_vehicle(driver)` / `list_driver_vehicle_history()` — latest or full history
- `GET /api/drivers/me/vehicle/` — current only
- `GET /api/drivers/me/vehicles/` — assignment history

## Mobile API flags (`VehicleSerializer`)

| Field | Purpose |
|-------|---------|
| `identity_locked` | Driver cannot PATCH make/model/year/VIN/capacity |
| `registration_verified` | Plate/VIN locked on resubmit form |
| `can_replace_vehicle` | Show replace action |
| `model_spec_id` | Pre-fill catalog on resubmit/replace |
| `approval_status`, `resubmit_reason` | UI copy and resubmit banner |

## Deploy

Run migration on Heroku (`truck-buddy`):

```bash
python manage.py migrate
```

Existing active vehicles are backfilled to `APPROVED` by migration `0009_vehicle_approval_status`.

## Backup branches

Before deploying lifecycle changes, create/push backup branches:

- `backup/vehicle-lifecycle-20260730` (backend + mobile)
