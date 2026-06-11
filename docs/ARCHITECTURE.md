# DeliveryApp Backend — Architecture

**Last updated:** June 12, 2026  
**Product focus:** v1.0 — single fleet (Admin, Driver, Customer)

Full architecture reference (layers, v1.0/v2.0 scope, RBAC migration): see **DeliveryAppMobile** repo `docs/ARCHITECTURE.md` or workspace `project-docs/ARCHITECTURE.md`.

**Cursor rules:** `.cursor/rules/layered-architecture.mdc`

**Key backend modules:**

| Module | Role |
|--------|------|
| `delivery/views.py` | Thin ViewSets — HTTP only |
| `delivery/vehicle_update.py` | SSOT for vehicle updates |
| `delivery/serializers.py` | Field validation |
| `delivery/permissions.py` | *(planned)* DRF RBAC |

**Prod QA:** Vehicle CRUD verified June 12, 2026 — commit `6b74039`.
