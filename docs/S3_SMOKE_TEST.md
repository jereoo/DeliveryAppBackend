# S3 compliance storage — smoke test

Verify your AWS bucket and IAM user work with the compliance upload flow.

## Quick run on Heroku (uses Config Vars you set)

```bash
heroku run python manage.py test_s3_storage -a truck-buddy
```

## Local run (set env first)

PowerShell:

```powershell
$env:AWS_STORAGE_BUCKET_NAME = "your-bucket-name"
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "your-secret"
$env:AWS_S3_REGION_NAME = "us-east-1"
cd C:\Users\360WEB\DeliveryAppBackend
python manage.py test_s3_storage
```

## What each step checks

| Step | Validates |
|------|-----------|
| `env_configured` | `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` present |
| `head_bucket` | Bucket exists and credentials can reach it |
| `put_object` | IAM allows `s3:PutObject` under `compliance/staging/...` |
| `get_object` | IAM allows `s3:GetObject` |
| `presigned_put_and_get` | Same path mobile uses (presigned PUT then GET) |
| `delete_object` | Cleanup test file (`s3:DeleteObject` — optional but included) |

Test objects use prefix `compliance/staging/smoke-test/` and are deleted after the run.

## Django test runner (optional)

```bash
set RUN_S3_INTEGRATION=1
python manage.py test tests.test_s3_integration -v 2
```

**Not run in GitHub Actions** unless you add secrets and `RUN_S3_INTEGRATION=1` — CI uses mocked S3 in `tests/test_compliance.py`.

## Common failures

| Error | Fix |
|-------|-----|
| `Set AWS_*` | Add Heroku Config Vars or local env |
| `404 / NoSuchBucket` | Wrong bucket name or region (`AWS_S3_REGION_NAME`) |
| `403 AccessDenied` on put/get | IAM policy must allow `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` on `arn:aws:s3:::BUCKET/compliance/*` |
| Presigned PUT HTTP 403 | Bucket policy blocking uploads; check Block Public Access (presigned is fine with private bucket) |

## Related

- `delivery/s3_smoke.py` — test implementation
- `delivery/compliance_storage.py` — production S3 helpers
- `docs/COMPLIANCE.md` — upload policy
