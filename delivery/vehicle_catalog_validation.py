"""Validation helpers for vehicle catalog lookups during registration."""

from __future__ import annotations

from django.core.exceptions import ValidationError

from .models import VehicleModelSpec
from .vehicle_constants import (
    MAX_VEHICLE_CAPACITY_KG,
    MAX_VEHICLE_CAPACITY_LB,
    max_vehicle_capacity_for_unit,
)

LB_TO_KG = 0.453592


def max_capacity_for_spec(spec: VehicleModelSpec, unit: str) -> int:
    """Effective max load: min(manufacturer rating, fleet policy cap)."""
    fleet_cap = max_vehicle_capacity_for_unit(unit)
    if unit == 'lb':
        return min(spec.max_payload_lb, fleet_cap)
    spec_kg = int(round(spec.max_payload_lb * LB_TO_KG))
    return min(spec_kg, fleet_cap)


def validate_model_year_for_spec(spec: VehicleModelSpec, year: int) -> None:
    if year < spec.start_year:
        raise ValidationError({
            'vehicle_year': (
                f'{spec.manufacturer.name} {spec.name} is available from {spec.start_year}.'
            ),
        })
    if spec.end_year is not None and year > spec.end_year:
        raise ValidationError({
            'vehicle_year': (
                f'{spec.manufacturer.name} {spec.name} was last sold in {spec.end_year}.'
            ),
        })


def validate_capacity_for_spec(spec: VehicleModelSpec, capacity: int, unit: str) -> None:
    if capacity <= 0:
        raise ValidationError({'vehicle_capacity': 'Capacity must be greater than 0.'})
    allowed = max_capacity_for_spec(spec, unit)
    if capacity > allowed:
        raise ValidationError({
            'vehicle_capacity': (
                f'Capacity cannot exceed {allowed} {unit} for '
                f'{spec.manufacturer.name} {spec.name} '
                f'(manufacturer max {spec.max_payload_lb} lb; '
                f'fleet max {MAX_VEHICLE_CAPACITY_KG} kg / {MAX_VEHICLE_CAPACITY_LB} lb).'
            ),
        })


def get_active_model_spec(spec_id: int) -> VehicleModelSpec:
    try:
        spec = VehicleModelSpec.objects.select_related('manufacturer').get(
            pk=spec_id,
            is_active=True,
            manufacturer__is_active=True,
        )
    except VehicleModelSpec.DoesNotExist as exc:
        raise ValidationError({
            'vehicle_model_spec_id': 'Select a valid vehicle make and model from the list.',
        }) from exc
    return spec
