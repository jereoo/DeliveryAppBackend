"""Staff vehicle approval and resubmit workflow."""

from __future__ import annotations

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .driver_utils import get_current_vehicle, get_driver_for_user
from .models import Vehicle, VehicleApprovalStatus
from .staff_constants import PERM_RESOURCES_WRITE
from .staff_permissions import require_staff_permission


def approve_vehicle(staff_user, vehicle: Vehicle) -> Vehicle:
    require_staff_permission(staff_user, PERM_RESOURCES_WRITE, message='Only staff with resource write permission may approve vehicles.')
    if vehicle.approval_status == VehicleApprovalStatus.APPROVED:
        raise ValidationError({'approval_status': 'Vehicle is already approved.'})
    if vehicle.approval_status == VehicleApprovalStatus.REJECTED:
        raise ValidationError({'approval_status': 'Rejected vehicles cannot be approved without staff review.'})

    vehicle.approval_status = VehicleApprovalStatus.APPROVED
    vehicle.active = True
    vehicle.resubmit_reason = None
    vehicle.approved_at = timezone.now()
    vehicle.approved_by = staff_user
    vehicle.save(update_fields=[
        'approval_status',
        'active',
        'resubmit_reason',
        'approved_at',
        'approved_by',
    ])
    return vehicle


def request_vehicle_resubmit(staff_user, vehicle: Vehicle, *, reason: str) -> Vehicle:
    """Staff sends an approved (or pending) vehicle back to the driver for correction."""
    require_staff_permission(staff_user, PERM_RESOURCES_WRITE, message='Only staff with resource write permission may request vehicle resubmit.')
    if not reason or not str(reason).strip():
        raise ValidationError({'resubmit_reason': 'Resubmit reason is required.'})
    if vehicle.approval_status == VehicleApprovalStatus.REJECTED:
        raise ValidationError({'approval_status': 'Vehicle is rejected; use a different workflow.'})

    vehicle.approval_status = VehicleApprovalStatus.RESUBMIT
    vehicle.active = False
    vehicle.resubmit_reason = str(reason).strip()
    vehicle.approved_at = None
    vehicle.approved_by = None
    vehicle.save(update_fields=[
        'approval_status',
        'active',
        'resubmit_reason',
        'approved_at',
        'approved_by',
    ])
    return vehicle


def driver_resubmit_vehicle(user, vehicle: Vehicle, *, data: dict) -> Vehicle:
    """
    Driver resubmits corrected vehicle data after staff RESUBMIT.
    Sets status back to PENDING; vehicle stays inactive until staff approves.
    """
    driver = get_driver_for_user(user)
    if not driver:
        raise PermissionDenied('Driver profile not found.')
    current = get_current_vehicle(driver)
    if not current or current.id != vehicle.id:
        raise PermissionDenied('You may only resubmit your currently assigned vehicle.')

    if vehicle.approval_status != VehicleApprovalStatus.RESUBMIT:
        raise ValidationError({'approval_status': 'Vehicle is not awaiting resubmit.'})

    from .vehicle_field_policy import apply_driver_vehicle_identity_update

    apply_driver_vehicle_identity_update(vehicle, data)
    vehicle.approval_status = VehicleApprovalStatus.PENDING
    vehicle.active = False
    vehicle.resubmit_reason = None
    vehicle.approved_at = None
    vehicle.approved_by = None
    vehicle.save()
    return vehicle
