"""Atomic driver vehicle replace (deactivate previous, assign new pending vehicle)."""

from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import ValidationError

from .driver_utils import get_current_assignment, get_current_vehicle
from .models import Driver, VehicleApprovalStatus
from .vehicle_onboarding_service import assign_vehicle_to_driver, create_vehicle_from_catalog
from .vehicle_utils import deactivate_vehicle


@transaction.atomic
def replace_driver_vehicle(
    driver: Driver,
    *,
    vehicle_model_spec_id: int,
    vehicle_year: int,
    vehicle_license_plate: str,
    vehicle_vin: str,
    vehicle_capacity: int,
    vehicle_capacity_unit: str,
) -> tuple:
    """
    Deactivate and close assignment on current vehicle, create a new pending vehicle,
    and assign it to the driver. Returns (new_vehicle, previous_vehicle_or_none).
    """
    current = get_current_vehicle(driver)
    if current and current.approval_status == VehicleApprovalStatus.RESUBMIT:
        raise ValidationError({
            'detail': 'Correct your current vehicle resubmit request before adding a replacement.',
        })

    previous = None
    assignment = get_current_assignment(driver)
    if assignment and assignment.vehicle_id:
        previous = assignment.vehicle
        deactivate_vehicle(previous, close_assignments=True)

    new_vehicle = create_vehicle_from_catalog(
        vehicle_model_spec_id=vehicle_model_spec_id,
        vehicle_year=vehicle_year,
        vehicle_license_plate=vehicle_license_plate,
        vehicle_vin=vehicle_vin,
        vehicle_capacity=vehicle_capacity,
        vehicle_capacity_unit=vehicle_capacity_unit,
        approval_status=VehicleApprovalStatus.PENDING,
        active=False,
    )
    assign_vehicle_to_driver(driver, new_vehicle)
    return new_vehicle, previous
