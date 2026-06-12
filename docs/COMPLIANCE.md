# Compliance — Driver & Vehicle Legal Documentation

**Last updated:** June 12, 2026  
**Phase:** 4A (registry + display; no assignment blocking)  
**Product scope:** v1.0 single fleet — Admin, Driver, Customer

---

## Purpose

Commercial delivery fleets must keep proof on file that:

1. The **driver** is licensed to operate the vehicle class used.
2. The **vehicle** is registered for road use.
3. The vehicle carries **commercial insurance** that covers delivery use.

Personal auto policies typically **exclude** commercial delivery. The system records metadata and optional file copies; it does **not** provide legal advice.

---

## Document types

| Type | Subject | Required for delivery (Phase 4B/4C) | Phase 4A |
|------|---------|--------------------------------------|----------|
| **Driver license** | Driver | Yes | Registry + verify |
| **Vehicle registration** | Vehicle | Yes | Registry + verify |
| **Commercial insurance** | Vehicle | Yes — must be `COMMERCIAL` coverage | Registry + verify |
| **Inspection** | Vehicle | Jurisdiction-dependent | Optional |

Stored in `LegalDocument` (`delivery/models.py`). Enums: `delivery/compliance_constants.py`.

---

## Minimum fields by document type

### Driver license

| Field | Required at upload | Notes |
|-------|-------------------|--------|
| `license_number` | Yes | Already on `Driver`; document record may duplicate for file linkage |
| `issuer` | Recommended | State/province DMV |
| `effective_date` | Optional | |
| `expiry_date` | Recommended | Required for verified status in Phase 4B |
| `file_key` / `file_name` | Optional | Scan/photo via presigned S3 upload |

### Vehicle registration

| Field | Required at upload | Notes |
|-------|-------------------|--------|
| `policy_number` or plate reference | Recommended | Registration number |
| `issuer` | Recommended | DMV / motor registry |
| `effective_date` | Optional | |
| `expiry_date` | Recommended | |
| `file_key` / `file_name` | Optional | |

### Commercial insurance

| Field | Required at upload | Notes |
|-------|-------------------|--------|
| `issuer` | **Yes** | Insurance carrier name |
| `policy_number` | **Yes** | |
| `coverage_type` | **Yes** | Must be `COMMERCIAL` for delivery eligibility (enforced Phase 4B/4C) |
| `effective_date` | Recommended | |
| `expiry_date` | **Yes** for verify | Admin cannot mark verified without expiry in Phase 4B |
| Named insured | In `notes` or file | Should match fleet operator / vehicle owner |
| Policy limits | In `notes` or file | e.g. liability $1M CSL — record for audit |

**Driver consent (upload UI):**

> I confirm this policy covers **commercial delivery use** and is not a personal auto policy only.

### Inspection (optional)

| Field | Notes |
|-------|--------|
| `issuer` | Licensed inspection station |
| `expiry_date` | Next due date |
| `file_key` | Certificate scan |

---

## Jurisdiction notes (US / CA)

Aligned with `Customer.address_country` (`US`, `CA`).

| Topic | United States | Canada |
|-------|---------------|--------|
| Driver license | State-issued; class must match vehicle | Provincial/territorial license |
| Registration | State DMV; plate tied to VIN | Provincial registration |
| Commercial insurance | Often required for hire/delivery; limits vary by state | Commercial fleet policies; provincial rules |
| Inspection | State-dependent (e.g. annual safety in some states) | Provincial programs (e.g. Ontario Safety Standards Certificate) |

**Phase 4A:** Record what the fleet operator provides; admin verifies. No automatic jurisdiction rules in code.

---

## Workflow & roles

| Action | Admin | Driver |
|--------|-------|--------|
| Upload / register metadata | Any driver/vehicle | Own profile + assigned vehicle only |
| View documents | All | Own only |
| Verify / reject | Yes | No |
| Download file | Yes | Own documents only |

**Status lifecycle:** `PENDING` → `VERIFIED` or `REJECTED`; `EXPIRED` set by nightly job in Phase 4B.

**Phase 4A:** No blocking of deliveries, assignments, or vehicle reactivation.

---

## File storage

- **Never** store uploads on Heroku ephemeral disk.
- **Production:** Private S3 bucket; presigned PUT for upload, presigned GET for download.
- **Env vars:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`
- Model fields: `file_key` (S3 object key), `file_name` (original filename).

---

## Retention

| Data | Retention guidance |
|------|-------------------|
| Verified documents | Retain **7 years** after expiry or driver/vehicle offboarding (adjust per counsel) |
| Rejected uploads | Retain **90 days** then delete file; keep metadata row with `REJECTED` |
| Audit fields | `verified_by`, `verified_at`, `created_at` — do not delete |

Implement automated purge in a later phase; Phase 4A is manual admin cleanup if needed.

---

## Verification checklist (admin)

Before marking **VERIFIED**:

- [ ] Document type matches subject (driver vs vehicle)
- [ ] For insurance: `coverage_type == COMMERCIAL`
- [ ] Expiry date is in the future (Phase 4B hard rule)
- [ ] Policy/registrant matches fleet records (VIN, plate, named insured)
- [ ] File readable (if uploaded)

---

## API (Phase 4A implementation)

See `DeliveryAppMobile/docs/PHASE_4A_LEGAL_COMPLIANCE.md` §7.

Business logic SSOT: `delivery/compliance_service.py` (Phase 4A #2).

---

## Disclaimer

This application aids **record-keeping and operational visibility**. It is not legal, insurance, or compliance advice. Fleet operators remain responsible for meeting federal, state/provincial, and carrier requirements.

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `DeliveryAppMobile/docs/PHASE_4A_LEGAL_COMPLIANCE.md` | Full technical spec |
| `DeliveryAppMobile/docs/PROJECT_PLAN.md` | Roadmap |
| `.cursor/rules/layered-architecture.mdc` | Layer boundaries |
