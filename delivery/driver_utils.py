"""Helpers for driver profile and current vehicle assignment."""

from django.db import models
from django.utils import timezone

from .models import Driver, DriverVehicle


def get_driver_for_user(user):
    """Return the Driver linked to this auth user, or None."""
    if not user or not user.is_authenticated:
        return None
    return Driver.objects.filter(user=user).first()


def get_current_assignment(driver):
    """Return the active DriverVehicle row for this driver, if any."""
    if not driver:
        return None
    today = timezone.now().date()
    return (
        DriverVehicle.objects.filter(driver=driver, assigned_from__lte=today)
        .filter(models.Q(assigned_to__isnull=True) | models.Q(assigned_to__gt=today))
        .select_related('vehicle')
        .order_by('-assigned_from')
        .first()
    )


def get_current_vehicle(driver):
    """Vehicle on the driver's open assignment (None if unassigned or assignment closed)."""
    assignment = get_current_assignment(driver)
    return assignment.vehicle if assignment else None


def get_driver_vehicle(driver):
    """
    Latest vehicle linked to this driver (includes inactive / ended assignments).
    Prefer get_current_vehicle() for dispatch and driver self-service UI.
    """
    if not driver:
        return None
    row = (
        DriverVehicle.objects.filter(driver=driver, vehicle__isnull=False)
        .select_related('vehicle')
        .order_by('-assigned_from')
        .first()
    )
    return row.vehicle if row else None


def list_driver_vehicle_history(driver):
    """All driver-vehicle assignment rows, newest first."""
    if not driver:
        return DriverVehicle.objects.none()
    return (
        DriverVehicle.objects.filter(driver=driver, vehicle__isnull=False)
        .select_related('vehicle')
        .order_by('-assigned_from')
    )
