# Compliance test documents (fictional)

**Not valid government or insurance documents.** For local development and QA upload flows only.

## Generate PDFs

```powershell
cd DeliveryAppBackend
python manage.py generate_compliance_test_pdfs
```

Creates:

| File | Document type | Suggested expiry |
|------|---------------|------------------|
| `driver_license_sample.pdf` | `DRIVER_LICENSE` | 2028-12-31 (see metadata.json) |
| `vehicle_registration_sample.pdf` | `VEHICLE_REGISTRATION` | 2027-12-31 |
| `commercial_insurance_sample.pdf` | `COMMERCIAL_INSURANCE` | 2027-12-31 |

See `metadata.json` for suggested form field values (issuer, policy #, etc.).

## How to test in the app

1. Log in as driver (or admin on vehicle/driver compliance panel).
2. Choose PDF → pick a file from this folder.
3. Enter expiry date and issuer/carrier from `metadata.json`.
4. Submit for review → log in as admin → Approve.

Every page is titled **SAMPLE … TEST ONLY — NOT VALID**.

## Cleanup misclassified uploads (pre-fix test data)

If registration/insurance PDFs were uploaded under **Legal documents — Driver** before the July 2026 fix, they were stored as driver licenses. Reject them on Heroku:

```powershell
heroku run python manage.py cleanup_misclassified_driver_documents -a truck-buddy
heroku run python manage.py cleanup_misclassified_driver_documents --apply -a truck-buddy
```

Dry-run lists matches; `--apply` rejects pending misclassified rows.
