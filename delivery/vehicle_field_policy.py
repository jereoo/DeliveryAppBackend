"""Field-level edit rules for vehicle identity (driver vs staff)."""

from __future__ import annotations

from rest_framework.exceptions import PermissionDenied, ValidationError

from .compliance_constants import DocumentStatus, DocumentType
from .models import LegalDocument, Vehicle, VehicleApprovalStatus
from .vehicle_catalog_validation import get_active_model_spec, validate_capacity_for_spec, validate_model_year_for_spec

IDENTITY_FIELDS = frozenset({
    'license_plate',
    'make',
    'model',
    'year',
    'vin',
    'capacity',
    'capacity_unit',
    'model_spec_id',
})


def vehicle_has_verified_registration(vehicle: Vehicle) -> bool:
    return LegalDocument.objects.filter(
        vehicle=vehicle,
        document_type=DocumentType.VEHICLE_REGISTRATION,
        status=DocumentStatus.VERIFIED,
    ).exists()


def identity_locked_for_driver(vehicle: Vehicle) -> bool:
    return vehicle.approval_status == VehicleApprovalStatus.APPROVED


def driver_may_replace_vehicle(vehicle: Vehicle | None) -> bool:
    if vehicle is None:
        return True
    return vehicle.approval_status in (
        VehicleApprovalStatus.APPROVED,
        VehicleApprovalStatus.PENDING,
        VehicleApprovalStatus.REJECTED,
    )


def filter_driver_vehicle_patch_data(vehicle: Vehicle, data: dict) -> dict:
    """Return only keys the driver may PATCH for this vehicle state."""
    if not data:
        return {}

    if vehicle.approval_status == VehicleApprovalStatus.RESUBMIT:
        allowed = set(IDENTITY_FIELDS)
    elif vehicle.approval_status == VehicleApprovalStatus.PENDING:
        allowed = set(IDENTITY_FIELDS)
    elif vehicle.approval_status == VehicleApprovalStatus.APPROVED:
        allowed = {'active'}
    else:
        allowed = set()

    if vehicle_has_verified_registration(vehicle):
        allowed -= {'vin', 'license_plate'}

    return {k: v for k, v in data.items() if k in allowed}


def assert_staff_may_edit_vehicle_fields(vehicle: Vehicle, data: dict) -> None:
    """Staff cannot mutate identity fields on approved vehicles (use resubmit instead)."""
    if not data:
        return
    if vehicle.approval_status != VehicleApprovalStatus.APPROVED:
        return
    if IDENTITY_FIELDS.intersection(data.keys()):
        raise PermissionDenied(
            'Approved vehicle identity cannot be edited. Request resubmit so the driver can correct data.'
        )


def apply_driver_vehicle_identity_update(vehicle: Vehicle, data: dict) -> None:
    """Apply catalog-backed identity updates during resubmit/pending correction."""
    spec_id = data.get('model_spec_id') or data.get('vehicle_model_spec_id')
    if spec_id is not None:
        spec = get_active_model_spec(int(spec_id))
        vehicle.model_spec = spec
        vehicle.make = spec.manufacturer.name
        vehicle.model = spec.name

    if 'year' in data:
        year = int(data['year'])
        spec = vehicle.model_spec
        if spec:
            validate_model_year_for_spec(spec, year)
        vehicle.year = year

    if 'license_plate' in data and not vehicle_has_verified_registration(vehicle):
        vehicle.license_plate = str(data['license_plate']).strip().upper()

    if 'vin' in data and not vehicle_has_verified_registration(vehicle):
        vin = str(data['vin']).strip().upper()
        if len(vin) != 17:
            raise ValidationError({'vin': 'VIN must be exactly 17 characters.'})
        vehicle.vin = vin

    if 'capacity' in data and 'capacity_unit' in data:
        capacity = int(data['capacity'])
        unit = data['capacity_unit']
        if vehicle.model_spec:
            validate_capacity_for_spec(vehicle.model_spec, capacity, unit)
        vehicle.capacity = capacity
        vehicle.capacity_unit = unit
