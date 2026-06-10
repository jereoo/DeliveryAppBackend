"""Shared vehicle field limits."""

MAX_VEHICLE_CAPACITY_KG = 2000
MAX_VEHICLE_CAPACITY_LB = 4400


def max_vehicle_capacity_for_unit(unit: str) -> int:
    """Return the fleet max load for kg or lb."""
    if unit == 'lb':
        return MAX_VEHICLE_CAPACITY_LB
    return MAX_VEHICLE_CAPACITY_KG
