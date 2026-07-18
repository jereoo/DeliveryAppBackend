"""Driver registration approval workflow (admin gate after self-registration)."""

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Driver, DriverApprovalStatus


def approve_driver(staff_user, driver: Driver) -> Driver:
    if not staff_user.is_staff:
        raise PermissionDenied('Only staff may approve drivers.')
    if driver.approval_status == DriverApprovalStatus.APPROVED:
        raise ValidationError({'approval_status': 'Driver is already approved.'})

    driver.approval_status = DriverApprovalStatus.APPROVED
    driver.active = True
    driver.approval_rejection_reason = None
    driver.approved_at = timezone.now()
    driver.approved_by = staff_user
    driver.save(update_fields=[
        'approval_status',
        'active',
        'approval_rejection_reason',
        'approved_at',
        'approved_by',
    ])
    return driver


def reject_driver(staff_user, driver: Driver, *, reason: str) -> Driver:
    if not staff_user.is_staff:
        raise PermissionDenied('Only staff may reject drivers.')
    if not reason or not str(reason).strip():
        raise ValidationError({'rejection_reason': 'Rejection reason is required.'})

    driver.approval_status = DriverApprovalStatus.REJECTED
    driver.active = False
    driver.approval_rejection_reason = str(reason).strip()
    driver.approved_at = None
    driver.approved_by = None
    driver.save(update_fields=[
        'approval_status',
        'active',
        'approval_rejection_reason',
        'approved_at',
        'approved_by',
    ])
    return driver
