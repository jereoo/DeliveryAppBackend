"""Shared test helper for vehicle catalog specs."""

from delivery.models import VehicleModelSpec


def get_catalog_spec_id(manufacturer: str = 'Ford', model: str = 'F-150') -> int:
    return VehicleModelSpec.objects.get(manufacturer__name=manufacturer, name=model).pk
