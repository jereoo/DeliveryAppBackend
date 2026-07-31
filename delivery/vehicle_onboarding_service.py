"""Create vehicles from catalog spec (registration and replace flows)."""

from __future__ import annotations

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Driver, DriverVehicle, Vehicle, VehicleApprovalStatus, VehicleModelSpec
from .vehicle_catalog_validation import (
    get_active_model_spec,
    validate_capacity_for_spec,
    validate_model_year_for_spec,
)


def create_vehicle_from_catalog(
    *,
    vehicle_model_spec_id: int,
    vehicle_year: int,
    vehicle_license_plate: str,
    vehicle_vin: str,
    vehicle_capacity: int,
    vehicle_capacity_unit: str,
    approval_status: str = VehicleApprovalStatus.PENDING,
    active: bool = False,
) -> Vehicle:
    """Single source of truth for catalog-backed vehicle creation."""
    spec = get_active_model_spec(vehicle_model_spec_id)
    validate_model_year_for_spec(spec, vehicle_year)
    validate_capacity_for_spec(spec, vehicle_capacity, vehicle_capacity_unit)

    plate = vehicle_license_plate.strip().upper()
    vin = vehicle_vin.strip().upper()
    if Vehicle.objects.filter(license_plate=plate).exists():
        raise ValidationError({'vehicle_license_plate': 'Vehicle with this license plate already exists.'})
    if Vehicle.objects.filter(vin=vin).exists():
        raise ValidationError({'vehicle_vin': 'Vehicle with this VIN already exists.'})

    return Vehicle.objects.create(
        license_plate=plate,
        model_spec=spec,
        make=spec.manufacturer.name,
        model=spec.name,
        year=vehicle_year,
        vin=vin,
        capacity=vehicle_capacity,
        capacity_unit=vehicle_capacity_unit,
        approval_status=approval_status,
        active=active,
    )


def assign_vehicle_to_driver(driver: Driver, vehicle: Vehicle, *, assigned_from=None) -> DriverVehicle:
    today = assigned_from or timezone.now().date()
    return DriverVehicle.objects.create(
        driver=driver,
        vehicle=vehicle,
        assigned_from=today,
    )
