"""S3 presigned URLs and upload validation for compliance documents (Phase 4A #4)."""

import os
import re
import uuid

from rest_framework.exceptions import ValidationError

COMPLIANCE_STAGING_PREFIX = 'compliance/staging'
ALLOWED_UPLOAD_CONTENT_TYPES = frozenset({'application/pdf'})
MAX_COMPLIANCE_FILE_BYTES = 10 * 1024 * 1024
PRESIGNED_UPLOAD_EXPIRES_SECONDS = 900
PRESIGNED_DOWNLOAD_EXPIRES_SECONDS = 900

_SAFE_FILENAME_RE = re.compile(r'[^A-Za-z0-9._-]+')
_AWS_REGION_RE = re.compile(r'([a-z]{2}-(?:gov-)?[a-z]+-\d+)')


def normalize_aws_region(raw: str | None) -> str:
    """Return a boto3-compatible region code (e.g. ca-central-1).

    Accepts console labels like 'Canada (Central) ca-central-1'.
    """
    value = (raw or '').strip()
    if not value:
        return 'us-east-1'
    match = _AWS_REGION_RE.search(value.lower())
    if match:
        return match.group(1)
    return value


def is_storage_configured() -> bool:
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', '').strip()
    access_key = os.environ.get('AWS_ACCESS_KEY_ID', '').strip()
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '').strip()
    return bool(bucket and access_key and secret_key)


def get_storage_config() -> dict:
    return {
        'bucket': os.environ.get('AWS_STORAGE_BUCKET_NAME', '').strip(),
        'region': normalize_aws_region(os.environ.get('AWS_S3_REGION_NAME')),
    }


def _get_s3_client():
    import boto3
    from botocore.config import Config

    config = get_storage_config()
    return boto3.client(
        's3',
        region_name=config['region'],
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', '').strip(),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', '').strip(),
        config=Config(signature_version='s3v4'),
    )


def sanitize_pdf_filename(file_name: str) -> str:
    base = os.path.basename((file_name or '').strip())
    if not base:
        raise ValidationError({'file_name': 'File name is required.'})
    if not base.lower().endswith('.pdf'):
        raise ValidationError({'file_name': 'Only PDF files are accepted (.pdf).'})
    stem, ext = base[:-4], base[-4:]
    safe_stem = _SAFE_FILENAME_RE.sub('_', stem).strip('._') or 'document'
    if len(safe_stem) > 200:
        safe_stem = safe_stem[:200]
    return f'{safe_stem}{ext.lower()}'


def validate_upload_request(*, file_name: str, content_type: str, file_size: int | None = None) -> str:
    normalized_type = (content_type or '').split(';', 1)[0].strip().lower()
    if normalized_type not in ALLOWED_UPLOAD_CONTENT_TYPES:
        raise ValidationError({
            'content_type': 'Only application/pdf uploads are accepted.',
        })
    safe_name = sanitize_pdf_filename(file_name)
    if file_size is not None:
        if file_size <= 0:
            raise ValidationError({'file_size': 'File size must be greater than zero.'})
        if file_size > MAX_COMPLIANCE_FILE_BYTES:
            raise ValidationError({
                'file_size': f'File exceeds maximum size of {MAX_COMPLIANCE_FILE_BYTES} bytes.',
            })
    return safe_name


def build_staging_file_key(user_id: int, file_name: str) -> str:
    safe_name = sanitize_pdf_filename(file_name)
    upload_id = uuid.uuid4().hex
    return f'{COMPLIANCE_STAGING_PREFIX}/{user_id}/{upload_id}/{safe_name}'


def assert_file_key_owned_by_user(user_id: int, file_key: str | None) -> None:
    if not file_key:
        return
    key = file_key.strip()
    if not key:
        return
    expected_prefix = f'{COMPLIANCE_STAGING_PREFIX}/{user_id}/'
    if not key.startswith(expected_prefix):
        raise ValidationError({
            'file_key': 'Invalid or unauthorized file reference.',
        })
    if '..' in key or key.startswith('/'):
        raise ValidationError({'file_key': 'Invalid file reference.'})


def generate_presigned_put_url(*, file_key: str, content_type: str) -> str:
    config = get_storage_config()
    client = _get_s3_client()
    return client.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': config['bucket'],
            'Key': file_key,
            'ContentType': content_type,
        },
        ExpiresIn=PRESIGNED_UPLOAD_EXPIRES_SECONDS,
    )


def generate_presigned_get_url(*, file_key: str) -> str:
    config = get_storage_config()
    client = _get_s3_client()
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': config['bucket'],
            'Key': file_key,
        },
        ExpiresIn=PRESIGNED_DOWNLOAD_EXPIRES_SECONDS,
    )
