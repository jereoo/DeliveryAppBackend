"""Centralized vehicle update with role-based authorization."""
from django.http import Http404
from rest_framework.exceptions import ValidationError

from .driver_utils import get_driver_for_user, get_current_assignment, get_driver_vehicle
from .serializers import DriverOwnedVehicleSerializer, VehicleSerializer


def user_can_update_vehicle(user, vehicle) -> bool:
    """Staff may edit any vehicle; drivers only their currently assigned vehicle."""
    if user.is_staff:
        return True
    driver = get_driver_for_user(user)
    if not driver:
        return False
    assigned = get_driver_vehicle(driver)
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
    assignment = get_current_assignment(driver)
    if not assignment or assignment.vehicle_id != vehicle.id:
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
    serializer_cls = serializer_class_for_user(user)
    serializer = serializer_cls(vehicle, data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    vehicle.refresh_from_db()
    return vehicle
