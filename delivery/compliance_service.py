"""Legal document compliance — business logic SSOT (Phase 4A)."""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .compliance_constants import (
    CoverageType,
    DocumentStatus,
    DocumentType,
    DRIVER_DOCUMENT_TYPES,
    VEHICLE_DOCUMENT_TYPES,
)
from . import compliance_storage
from .driver_utils import get_driver_for_user, get_driver_vehicle
from .models import Driver, LegalDocument, Vehicle

REQUIRED_COMPLIANCE_TYPES = (
    DocumentType.DRIVER_LICENSE,
    DocumentType.VEHICLE_REGISTRATION,
    DocumentType.COMMERCIAL_INSURANCE,
)

MISCLASSIFIED_DRIVER_LICENSE_FILENAME_HINTS = (
    'commercial_insurance',
    'vehicle_registration',
    'insurance_sample',
    'registration_sample',
    'vehicle_inspection',
)


def user_can_access_driver(user, driver: Driver) -> bool:
    if user.is_staff:
        return True
    my_driver = get_driver_for_user(user)
    return my_driver is not None and my_driver.id == driver.id


def user_can_access_vehicle(user, vehicle: Vehicle) -> bool:
    if user.is_staff:
        return True
    driver = get_driver_for_user(user)
    if not driver:
        return False
    assigned = get_driver_vehicle(driver)
    return assigned is not None and assigned.id == vehicle.id


def user_can_access_document(user, document: LegalDocument) -> bool:
    if user.is_staff:
        return True
    if document.driver_id:
        return user_can_access_driver(user, document.driver)
    if document.vehicle_id:
        return user_can_access_vehicle(user, document.vehicle)
    return False


def assert_can_manage_driver_documents(user, driver: Driver):
    if not user_can_access_driver(user, driver):
        raise NotFound()


def assert_can_manage_vehicle_documents(user, vehicle: Vehicle):
    if not user_can_access_vehicle(user, vehicle):
        raise NotFound()


def get_document_or_404(document_id: int) -> LegalDocument:
    try:
        return LegalDocument.objects.get(pk=document_id)
    except LegalDocument.DoesNotExist as exc:
        raise NotFound() from exc


def create_document(user, *, driver=None, vehicle=None, data: dict) -> LegalDocument:
    doc_type = data.get('document_type')
    if not doc_type:
        raise ValidationError({'document_type': 'This field is required.'})

    if doc_type in DRIVER_DOCUMENT_TYPES:
        if not driver:
            raise ValidationError({'driver': 'Driver is required for this document type.'})
        assert_can_manage_driver_documents(user, driver)
        subject_driver = driver
        subject_vehicle = None
    elif doc_type in VEHICLE_DOCUMENT_TYPES:
        if not vehicle:
            raise ValidationError({'vehicle': 'Vehicle is required for this document type.'})
        assert_can_manage_vehicle_documents(user, vehicle)
        subject_driver = None
        subject_vehicle = vehicle
    else:
        raise ValidationError({'document_type': 'Invalid document type.'})

    file_key = data.get('file_key')
    compliance_storage.assert_file_key_owned_by_user(user.id, file_key)

    document = LegalDocument(
        document_type=doc_type,
        driver=subject_driver,
        vehicle=subject_vehicle,
        policy_number=data.get('policy_number'),
        issuer=data.get('issuer'),
        coverage_type=data.get('coverage_type'),
        effective_date=data.get('effective_date'),
        expiry_date=data.get('expiry_date'),
        file_key=file_key,
        file_name=data.get('file_name'),
        notes=data.get('notes'),
        status=DocumentStatus.PENDING,
    )
    document.full_clean()
    document.save()
    return document


def list_driver_owned_documents(driver: Driver):
    """Documents stored on the driver record (driver license)."""
    return LegalDocument.objects.filter(driver=driver).order_by('-created_at')


def list_documents_for_driver(driver: Driver):
    """All compliance docs for summary checks: driver license + assigned vehicle docs."""
    vehicle = get_driver_vehicle(driver)
    query = Q(driver=driver)
    if vehicle:
        query |= Q(vehicle=vehicle)
    return LegalDocument.objects.filter(query).order_by('-created_at')


def list_documents_for_vehicle(vehicle: Vehicle):
    return LegalDocument.objects.filter(vehicle=vehicle).order_by('-created_at')


def _verified_doc_exists(docs, doc_type, *, driver_id=None, vehicle_id=None) -> bool:
    today = timezone.now().date()
    for doc in docs:
        if doc.document_type != doc_type or doc.status != DocumentStatus.VERIFIED:
            continue
        if doc.expiry_date and doc.expiry_date < today:
            continue
        if doc.document_type == DocumentType.COMMERCIAL_INSURANCE:
            if doc.coverage_type != CoverageType.COMMERCIAL:
                continue
        if driver_id is not None and doc.driver_id != driver_id:
            continue
        if vehicle_id is not None and doc.vehicle_id != vehicle_id:
            continue
        if doc.document_type in (
            DocumentType.DRIVER_LICENSE,
            DocumentType.VEHICLE_REGISTRATION,
            DocumentType.COMMERCIAL_INSURANCE,
        ) and not doc.expiry_date:
            continue
        return True
    return False


def get_compliance_summary(driver: Driver) -> dict:
    docs = list(list_documents_for_driver(driver))
    today = timezone.now().date()
    expiring_cutoff = today + timedelta(days=30)

    summary = {
        'pending': 0,
        'verified': 0,
        'rejected': 0,
        'expired': 0,
        'expiring_soon': 0,
        'missing_types': [],
        'is_fully_compliant': False,
    }

    for doc in docs:
        key = doc.status.lower()
        summary[key] = summary.get(key, 0) + 1
        if doc.status == DocumentStatus.VERIFIED and doc.expiry_date:
            if today <= doc.expiry_date <= expiring_cutoff:
                summary['expiring_soon'] += 1

    vehicle = get_driver_vehicle(driver)
    for doc_type in REQUIRED_COMPLIANCE_TYPES:
        if doc_type == DocumentType.DRIVER_LICENSE:
            has = _verified_doc_exists(docs, doc_type, driver_id=driver.id)
        elif vehicle:
            has = _verified_doc_exists(docs, doc_type, vehicle_id=vehicle.id)
        else:
            has = False
        if not has:
            summary['missing_types'].append(doc_type)

    summary['is_fully_compliant'] = (
        len(summary['missing_types']) == 0 and summary.get('expired', 0) == 0
    )
    return summary


def update_document(user, document: LegalDocument, data: dict) -> LegalDocument:
    if not user_can_access_document(user, document):
        raise NotFound()
    if not user.is_staff and document.status != DocumentStatus.PENDING:
        raise PermissionDenied('Only pending documents can be edited.')

    editable = (
        'policy_number', 'issuer', 'coverage_type', 'effective_date',
        'expiry_date', 'file_key', 'file_name', 'notes',
    )
    for field in editable:
        if field in data:
            setattr(document, field, data[field])
    if 'file_key' in data:
        compliance_storage.assert_file_key_owned_by_user(user.id, document.file_key)
    document.full_clean()
    document.save()
    return document


def _require_expiry_for_verify(document: LegalDocument):
    """Phase 4B — verified docs must have a future-facing expiry date."""
    if document.document_type in (
        DocumentType.COMMERCIAL_INSURANCE,
        DocumentType.VEHICLE_REGISTRATION,
        DocumentType.DRIVER_LICENSE,
    ) and not document.expiry_date:
        raise ValidationError({
            'expiry_date': f'Expiry date is required for {document.document_type}.',
        })


def _expire_superseded_verified(document: LegalDocument):
    """Mark other verified docs of the same type/subject as EXPIRED when a new one is verified."""
    if document.document_type not in (
        DocumentType.COMMERCIAL_INSURANCE,
        DocumentType.VEHICLE_REGISTRATION,
        DocumentType.DRIVER_LICENSE,
    ):
        return
    qs = LegalDocument.objects.filter(
        document_type=document.document_type,
        status=DocumentStatus.VERIFIED,
    ).exclude(pk=document.pk)
    if document.vehicle_id:
        qs = qs.filter(vehicle_id=document.vehicle_id)
    elif document.driver_id:
        qs = qs.filter(driver_id=document.driver_id)
    else:
        return
    qs.update(status=DocumentStatus.EXPIRED)


def mark_verified(staff_user, document_id: int, notes=None) -> LegalDocument:
    if not staff_user.is_staff:
        raise PermissionDenied('Only staff can verify documents.')

    document = get_document_or_404(document_id)
    _require_expiry_for_verify(document)

    if document.document_type == DocumentType.COMMERCIAL_INSURANCE:
        if document.coverage_type != CoverageType.COMMERCIAL:
            raise ValidationError({
                'coverage_type': 'Commercial insurance must have COMMERCIAL coverage type.',
            })

    _expire_superseded_verified(document)

    document.status = DocumentStatus.VERIFIED
    document.verified_by = staff_user
    document.verified_at = timezone.now()
    document.rejection_reason = None
    if notes is not None:
        document.notes = notes
    document.save()
    return document


def mark_rejected(staff_user, document_id: int, reason: str) -> LegalDocument:
    if not staff_user.is_staff:
        raise PermissionDenied('Only staff can reject documents.')

    document = get_document_or_404(document_id)
    if not reason:
        raise ValidationError({'rejection_reason': 'Rejection reason is required.'})

    document.status = DocumentStatus.REJECTED
    document.rejection_reason = reason
    document.verified_by = staff_user
    document.verified_at = timezone.now()
    document.save()
    return document


def _vehicle_has_current_verified(vehicle: Vehicle, doc_type: str, *, today=None) -> bool:
    today = today or timezone.now().date()
    qs = LegalDocument.objects.filter(
        vehicle=vehicle,
        document_type=doc_type,
        status=DocumentStatus.VERIFIED,
        expiry_date__gte=today,
    )
    if doc_type == DocumentType.COMMERCIAL_INSURANCE:
        qs = qs.filter(coverage_type=CoverageType.COMMERCIAL)
    return qs.exists()


def _vehicle_has_expired_doc(vehicle: Vehicle, doc_type: str, *, today=None) -> bool:
    today = today or timezone.now().date()
    return LegalDocument.objects.filter(
        vehicle=vehicle,
        document_type=doc_type,
    ).filter(
        Q(status=DocumentStatus.EXPIRED)
        | Q(status=DocumentStatus.VERIFIED, expiry_date__lt=today),
    ).exists()


def get_vehicle_reactivation_blockers(vehicle: Vehicle) -> list[str]:
    """Return machine-readable codes blocking vehicle reactivation (Phase 4B)."""
    today = timezone.now().date()
    blockers: list[str] = []
    checks = (
        (DocumentType.VEHICLE_REGISTRATION, 'vehicle_registration_missing', 'vehicle_registration_expired'),
        (DocumentType.COMMERCIAL_INSURANCE, 'commercial_insurance_missing', 'commercial_insurance_expired'),
    )
    for doc_type, missing_code, expired_code in checks:
        if _vehicle_has_current_verified(vehicle, doc_type, today=today):
            continue
        if _vehicle_has_expired_doc(vehicle, doc_type, today=today):
            blockers.append(expired_code)
        else:
            blockers.append(missing_code)
    return blockers


def assert_vehicle_may_reactivate(vehicle: Vehicle):
    blockers = get_vehicle_reactivation_blockers(vehicle)
    if blockers:
        raise ValidationError({'compliance': blockers})


def mark_expired_documents(as_of_date=None) -> int:
    """Mark VERIFIED documents past expiry as EXPIRED. Returns count updated."""
    as_of = as_of_date or timezone.now().date()
    return LegalDocument.objects.filter(
        status=DocumentStatus.VERIFIED,
        expiry_date__lt=as_of,
    ).update(status=DocumentStatus.EXPIRED)


def is_vehicle_compliant(vehicle: Vehicle) -> dict:
    """Current verified registration + commercial insurance (Phase 4B)."""
    today = timezone.now().date()
    has_registration = _vehicle_has_current_verified(
        vehicle, DocumentType.VEHICLE_REGISTRATION, today=today,
    )
    has_insurance = _vehicle_has_current_verified(
        vehicle, DocumentType.COMMERCIAL_INSURANCE, today=today,
    )
    blockers = get_vehicle_reactivation_blockers(vehicle)
    return {
        'compliant': has_registration and has_insurance,
        'registration': has_registration,
        'insurance': has_insurance,
        'blockers': blockers,
        'may_reactivate': len(blockers) == 0,
    }


def is_driver_eligible_for_dispatch(driver: Driver) -> dict:
    """Phase 4C — driver + assigned vehicle must be compliant for delivery assignment."""
    blockers = get_dispatch_eligibility_blockers(driver)
    return {
        'eligible': len(blockers) == 0,
        'blockers': blockers,
        'summary': get_compliance_summary(driver),
    }


def get_dispatch_eligibility_blockers(driver: Driver) -> list[str]:
    """Machine-readable codes blocking dispatch assignment (Phase 4C)."""
    blockers: list[str] = []
    if not driver.active:
        blockers.append('driver_inactive')

    vehicle = get_driver_vehicle(driver)
    if not vehicle:
        blockers.append('no_vehicle_assigned')
    elif not vehicle.active:
        blockers.append('vehicle_inactive')

    today = timezone.now().date()
    docs = list(list_documents_for_driver(driver))
    if not _verified_doc_exists(docs, DocumentType.DRIVER_LICENSE, driver_id=driver.id):
        if _subject_has_expired_doc(driver_id=driver.id, doc_type=DocumentType.DRIVER_LICENSE, today=today):
            blockers.append('driver_license_expired')
        else:
            blockers.append('driver_license_missing')

    if vehicle:
        blockers.extend(get_vehicle_reactivation_blockers(vehicle))

    return blockers


def assert_driver_eligible_for_dispatch(driver: Driver):
    blockers = get_dispatch_eligibility_blockers(driver)
    if blockers:
        raise ValidationError({'compliance': blockers})


def is_misclassified_driver_license_document(document: LegalDocument) -> bool:
    """True when a driver-license row looks like registration/insurance uploaded to the wrong panel."""
    if document.document_type != DocumentType.DRIVER_LICENSE or not document.driver_id:
        return False
    if document.status not in (DocumentStatus.PENDING, DocumentStatus.REJECTED):
        return False
    if document.coverage_type:
        return True
    if document.policy_number and str(document.policy_number).strip():
        return True
    file_name = (document.file_name or '').lower()
    return any(hint in file_name for hint in MISCLASSIFIED_DRIVER_LICENSE_FILENAME_HINTS)


def find_misclassified_driver_documents():
    candidates = LegalDocument.objects.filter(
        document_type=DocumentType.DRIVER_LICENSE,
        driver__isnull=False,
        status__in=(DocumentStatus.PENDING, DocumentStatus.REJECTED),
    ).select_related('driver').order_by('driver_id', '-created_at')
    return [doc for doc in candidates if is_misclassified_driver_license_document(doc)]


def reject_misclassified_driver_documents(staff_user, *, reason: str) -> int:
    if not staff_user.is_staff:
        raise PermissionDenied('Staff required.')
    count = 0
    for document in find_misclassified_driver_documents():
        if document.status == DocumentStatus.REJECTED:
            continue
        mark_rejected(staff_user, document.id, reason)
        count += 1
    return count


def _subject_has_expired_doc(*, driver_id=None, vehicle_id=None, doc_type: str, today) -> bool:
    query = LegalDocument.objects.filter(document_type=doc_type)
    if driver_id is not None:
        query = query.filter(driver_id=driver_id)
    if vehicle_id is not None:
        query = query.filter(vehicle_id=vehicle_id)
    return query.filter(
        Q(status=DocumentStatus.EXPIRED)
        | Q(status=DocumentStatus.VERIFIED, expiry_date__lt=today),
    ).exists()


def get_presigned_upload_url(
    user,
    *,
    file_name: str,
    content_type: str,
    file_size: int | None = None,
) -> dict:
    """Return presigned S3 PUT URL when storage is configured (Phase 4A #4.2)."""
    if not user.is_authenticated:
        raise PermissionDenied()

    if not compliance_storage.is_storage_configured():
        raise ValidationError({
            'storage': 'File upload is not configured. Submit metadata only.',
        })

    safe_name = compliance_storage.validate_upload_request(
        file_name=file_name,
        content_type=content_type,
        file_size=file_size,
    )
    normalized_type = content_type.split(';', 1)[0].strip().lower()
    file_key = compliance_storage.build_staging_file_key(user.id, safe_name)
    upload_url = compliance_storage.generate_presigned_put_url(
        file_key=file_key,
        content_type=normalized_type,
    )
    return {
        'upload_url': upload_url,
        'file_key': file_key,
        'file_name': safe_name,
        'content_type': normalized_type,
        'expires_in': compliance_storage.PRESIGNED_UPLOAD_EXPIRES_SECONDS,
        'max_size_bytes': compliance_storage.MAX_COMPLIANCE_FILE_BYTES,
    }


def upload_compliance_file(
    user,
    *,
    file_name: str,
    content_type: str,
    file_body: bytes,
) -> dict:
    """Upload PDF via Django (avoids browser S3 CORS). Phase 4A #4.5."""
    if not user.is_authenticated:
        raise PermissionDenied()
    return compliance_storage.upload_staging_object(
        user_id=user.id,
        file_name=file_name,
        content_type=content_type,
        file_body=file_body,
    )


def get_presigned_download_url(user, document: LegalDocument) -> dict:
    """Return presigned S3 GET URL for an attached compliance file (Phase 4A #4.2)."""
    if not user_can_access_document(user, document):
        raise NotFound()
    if not document.file_key:
        raise ValidationError({'file_key': 'No file attached to this document.'})
    if not compliance_storage.is_storage_configured():
        raise ValidationError({
            'storage': 'File download is not configured.',
        })

    download_url = compliance_storage.generate_presigned_get_url(file_key=document.file_key)
    return {
        'download_url': download_url,
        'file_name': document.file_name or 'document.pdf',
        'expires_in': compliance_storage.PRESIGNED_DOWNLOAD_EXPIRES_SECONDS,
    }
