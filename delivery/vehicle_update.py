"""Centralized vehicle update with role-based authorization."""

from django.http import Http404
from rest_framework.exceptions import ValidationError

from .driver_utils import get_current_vehicle, get_driver_for_user
from .serializers import DriverOwnedVehicleSerializer, VehicleSerializer
from .vehicle_field_policy import (
    assert_staff_may_edit_vehicle_fields,
    filter_driver_vehicle_patch_data,
    identity_locked_for_driver,
)


def user_can_update_vehicle(user, vehicle) -> bool:
    """Staff may edit any vehicle; drivers only their current assigned vehicle."""
    if user.is_staff:
        return True
    driver = get_driver_for_user(user)
    if not driver:
        return False
    assigned = get_current_vehicle(driver)
    return assigned is not None and assigned.id == vehicle.id


def user_can_read_vehicle(user, vehicle) -> bool:
    return user_can_update_vehicle(user, vehicle)


def assert_can_update_vehicle(user, vehicle):
    if not user_can_update_vehicle(user, vehicle):
        raise Http404()


def assert_driver_may_edit_vehicle(user, vehicle):
    """Drivers cannot edit inactive vehicles when assignment is no longer current."""
    if user.is_staff:
        return
    driver = get_driver_for_user(user)
    if not driver:
        raise Http404()
    current = get_current_vehicle(driver)
    if not current or current.id != vehicle.id:
        if not vehicle.active:
            raise ValidationError({
                'error': 'Vehicle is inactive. Contact admin to reactivate before editing.',
            })


def serializer_class_for_user(user):
    if user.is_staff:
        return VehicleSerializer
    return DriverOwnedVehicleSerializer


def serialize_vehicle_for_user(user, vehicle):
    return serializer_class_for_user(user)(vehicle).data


def update_vehicle(user, vehicle, data, *, partial=True):
    """
    Update a vehicle if the user is authorized.
    Staff uses VehicleSerializer; drivers use DriverOwnedVehicleSerializer.
    """
    assert_can_update_vehicle(user, vehicle)
    assert_driver_may_edit_vehicle(user, vehicle)

    if user.is_staff:
        assert_staff_may_edit_vehicle_fields(vehicle, data)
    else:
        data = filter_driver_vehicle_patch_data(vehicle, data)
        if not data:
            if identity_locked_for_driver(vehicle):
                raise ValidationError({
                    'detail': 'Vehicle identity is locked after approval. Upload compliance documents or wait for staff resubmit instructions.',
                })
            raise ValidationError({'detail': 'No editable fields in this request.'})

    serializer_cls = serializer_class_for_user(user)
    serializer = serializer_cls(vehicle, data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    vehicle.refresh_from_db()
    return vehicle
