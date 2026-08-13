"""Driver registration approval workflow (admin gate after self-registration)."""

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Driver, DriverApprovalStatus
from .staff_constants import PERM_DRIVERS_APPROVE
from .staff_permissions import require_staff_permission


def approve_driver(staff_user, driver: Driver) -> Driver:
    require_staff_permission(staff_user, PERM_DRIVERS_APPROVE, message='Only staff with driver approval permission may approve drivers.')
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
    require_staff_permission(staff_user, PERM_DRIVERS_APPROVE, message='Only staff with driver approval permission may reject drivers.')
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
