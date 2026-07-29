"""Compliance document expiry email reminders (Phase 4D)."""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from delivery.compliance_constants import DocumentStatus, DocumentType
from delivery.models import Driver, DriverVehicle, LegalDocument

COMPLIANCE_REMINDER_DAYS = (30, 14, 0)

_REMINDER_SENT_FIELD = {
    30: 'expiry_reminder_30_sent_at',
    14: 'expiry_reminder_14_sent_at',
    0: 'expiry_reminder_0_sent_at',
}

_DOCUMENT_TYPE_LABEL = {
    DocumentType.DRIVER_LICENSE: 'Driver license',
    DocumentType.VEHICLE_REGISTRATION: 'Vehicle registration',
    DocumentType.COMMERCIAL_INSURANCE: 'Commercial insurance',
    DocumentType.INSPECTION: 'Inspection',
}


def clear_expiry_reminder_fields(document: LegalDocument) -> None:
    """Reset reminder tracking when a document is re-verified or expiry changes."""
    document.expiry_reminder_30_sent_at = None
    document.expiry_reminder_14_sent_at = None
    document.expiry_reminder_0_sent_at = None


def _driver_display_name(driver: Driver | None) -> str:
    if not driver:
        return 'Driver'
    name = f'{driver.first_name} {driver.last_name}'.strip()
    if name:
        return name
    if driver.user_id and (driver.user.first_name or driver.user.last_name):
        return f'{driver.user.first_name} {driver.user.last_name}'.strip()
    return f'Driver #{driver.id}'


def resolve_driver_for_document(document: LegalDocument) -> Driver | None:
    if document.driver_id:
        return document.driver
    if not document.vehicle_id:
        return None
    assignment = (
        DriverVehicle.objects.filter(vehicle_id=document.vehicle_id, assigned_to__isnull=True)
        .select_related('driver', 'driver__user')
        .order_by('-assigned_from')
        .first()
    )
    return assignment.driver if assignment else None


def recipient_email_for_document(document: LegalDocument) -> str | None:
    driver = resolve_driver_for_document(document)
    if not driver or not driver.user_id:
        return None
    email = (driver.user.email or '').strip()
    return email or None


def _reminder_subject(document: LegalDocument, days_before: int) -> str:
    label = _DOCUMENT_TYPE_LABEL.get(document.document_type, document.document_type)
    if days_before == 0:
        return f'Action required: {label} expires today'
    return f'Reminder: {label} expires in {days_before} days'


def _reminder_body(document: LegalDocument, *, driver_name: str, days_before: int) -> str:
    label = _DOCUMENT_TYPE_LABEL.get(document.document_type, document.document_type)
    expiry = document.expiry_date.isoformat() if document.expiry_date else 'unknown'
    if days_before == 0:
        urgency = 'expires today'
    else:
        urgency = f'expires in {days_before} days (on {expiry})'

    lines = [
        f'Hello {driver_name},',
        '',
        f'Your {label} {urgency}.',
        '',
        'Upload an updated document in the DeliveryApp driver portal before the expiry date '
        'to avoid assignment delays.',
        '',
        'If you already submitted a replacement document, you can ignore this message while '
        'admin review is pending.',
        '',
        '— TruckBuddy / DeliveryApp',
    ]
    return '\n'.join(lines)


def send_compliance_expiry_reminders(*, as_of_date=None, dry_run: bool = False) -> dict:
    """
    Email drivers at 30, 14, and 0 days before verified document expiry.
    Each threshold fires at most once per document (tracked on LegalDocument).
    """
    today = as_of_date or timezone.now().date()
    sent_by_day = {30: 0, 14: 0, 0: 0}
    skipped_no_email = 0

    for days_before in COMPLIANCE_REMINDER_DAYS:
        target_expiry = today + timedelta(days=days_before)
        sent_field = _REMINDER_SENT_FIELD[days_before]
        documents = (
            LegalDocument.objects.filter(
                status=DocumentStatus.VERIFIED,
                expiry_date=target_expiry,
                **{f'{sent_field}__isnull': True},
            )
            .select_related('driver', 'driver__user', 'vehicle')
        )

        for document in documents:
            email = recipient_email_for_document(document)
            if not email:
                skipped_no_email += 1
                continue

            driver = resolve_driver_for_document(document)
            driver_name = _driver_display_name(driver)
            subject = _reminder_subject(document, days_before)
            body = _reminder_body(document, driver_name=driver_name, days_before=days_before)

            if dry_run:
                sent_by_day[days_before] += 1
                continue

            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            setattr(document, sent_field, timezone.now())
            document.save(update_fields=[sent_field])
            sent_by_day[days_before] += 1

    return {
        'as_of_date': today.isoformat(),
        'sent': sent_by_day,
        'skipped_no_email': skipped_no_email,
    }
