"""Live S3 smoke tests for compliance document storage (Phase 4A #4.1).

Run via: python manage.py test_s3_storage
Optional CI: RUN_S3_INTEGRATION=1 python manage.py test tests.test_s3_integration
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Callable
from urllib import error, request

from delivery import compliance_storage

# Minimal valid-enough PDF header for upload validation paths.
SMOKE_PDF_BYTES = b'%PDF-1.4\n% DeliveryApp S3 smoke test\n'
SMOKE_CONTENT_TYPE = 'application/pdf'
SMOKE_USER_ID = 0


@dataclass
class SmokeStepResult:
    name: str
    ok: bool
    detail: str = ''

    def as_dict(self) -> dict:
        return {'name': self.name, 'ok': self.ok, 'detail': self.detail}


def _step(name: str, fn: Callable[[], str]) -> SmokeStepResult:
    try:
        detail = fn()
        return SmokeStepResult(name=name, ok=True, detail=detail)
    except Exception as exc:
        return SmokeStepResult(name=name, ok=False, detail=str(exc))


def _check_env_configured() -> str:
    if not compliance_storage.is_storage_configured():
        raise RuntimeError(
            'Set AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, and AWS_SECRET_ACCESS_KEY.',
        )
    config = compliance_storage.get_storage_config()
    return f'bucket={config["bucket"]} region={config["region"]}'


def run_s3_smoke_tests() -> list[SmokeStepResult]:
    """Exercise bucket access, direct SDK I/O, and presigned PUT/GET."""
    config = compliance_storage.get_storage_config()
    smoke_key = compliance_storage.build_staging_file_key(SMOKE_USER_ID, 'smoke-test.pdf')
    smoke_key = smoke_key.replace(
        f'{compliance_storage.COMPLIANCE_STAGING_PREFIX}/{SMOKE_USER_ID}/',
        f'{compliance_storage.COMPLIANCE_STAGING_PREFIX}/smoke-test/',
        1,
    )
    results: list[SmokeStepResult] = []

    results.append(_step('env_configured', _check_env_configured))
    if not results[-1].ok:
        return results

    client = compliance_storage._get_s3_client()
    bucket = config['bucket']

    results.append(_step(
        'head_bucket',
        lambda: _head_bucket(client, bucket),
    ))
    if not results[-1].ok:
        return results

    results.append(_step(
        'put_object',
        lambda: _put_object(client, bucket, smoke_key),
    ))
    if not results[-1].ok:
        return results

    results.append(_step(
        'get_object',
        lambda: _get_object(client, bucket, smoke_key),
    ))

    results.append(_step(
        'presigned_put_and_get',
        lambda: _presigned_round_trip(bucket, smoke_key),
    ))

    results.append(_step(
        'delete_object',
        lambda: _delete_object(client, bucket, smoke_key),
    ))

    return results


def format_smoke_report(results: list[SmokeStepResult]) -> str:
    lines = ['S3 compliance storage smoke test', '']
    for item in results:
        status = 'PASS' if item.ok else 'FAIL'
        lines.append(f'  [{status}] {item.name}')
        if item.detail:
            lines.append(f'         {item.detail}')
    passed = sum(1 for r in results if r.ok)
    lines.append('')
    lines.append(f'Result: {passed}/{len(results)} passed')
    return '\n'.join(lines)


def all_passed(results: list[SmokeStepResult]) -> bool:
    return bool(results) and all(r.ok for r in results)


def _head_bucket(client, bucket: str) -> str:
    client.head_bucket(Bucket=bucket)
    return f'Bucket {bucket!r} is reachable'


def _put_object(client, bucket: str, key: str) -> str:
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=SMOKE_PDF_BYTES,
        ContentType=SMOKE_CONTENT_TYPE,
    )
    return f'Wrote {len(SMOKE_PDF_BYTES)} bytes to {key}'


def _get_object(client, bucket: str, key: str) -> str:
    response = client.get_object(Bucket=bucket, Key=key)
    body = response['Body'].read()
    if body != SMOKE_PDF_BYTES:
        raise RuntimeError(f'GET body mismatch ({len(body)} bytes)')
    return f'Read back {len(body)} bytes from {key}'


def _presigned_round_trip(bucket: str, base_key: str) -> str:
    presigned_key = base_key.replace('smoke-test.pdf', f'presigned-{uuid.uuid4().hex}.pdf')
    put_url = compliance_storage.generate_presigned_put_url(
        file_key=presigned_key,
        content_type=SMOKE_CONTENT_TYPE,
    )
    put_req = request.Request(
        put_url,
        data=SMOKE_PDF_BYTES,
        method='PUT',
        headers={'Content-Type': SMOKE_CONTENT_TYPE},
    )
    try:
        with request.urlopen(put_req, timeout=30) as resp:
            if resp.status not in (200, 204):
                raise RuntimeError(f'Presigned PUT returned HTTP {resp.status}')
    except error.HTTPError as exc:
        raise RuntimeError(f'Presigned PUT failed: HTTP {exc.code} {exc.reason}') from exc

    get_url = compliance_storage.generate_presigned_get_url(file_key=presigned_key)
    try:
        with request.urlopen(get_url, timeout=30) as resp:
            body = resp.read()
            if body != SMOKE_PDF_BYTES:
                raise RuntimeError(f'Presigned GET body mismatch ({len(body)} bytes)')
    except error.HTTPError as exc:
        raise RuntimeError(f'Presigned GET failed: HTTP {exc.code} {exc.reason}') from exc

    client = compliance_storage._get_s3_client()
    client.delete_object(Bucket=bucket, Key=presigned_key)
    return f'Presigned PUT/GET OK for {presigned_key}'


def _delete_object(client, bucket: str, key: str) -> str:
    client.delete_object(Bucket=bucket, Key=key)
    return f'Deleted {key}'
