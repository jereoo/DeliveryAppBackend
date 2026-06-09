"""Vehicle lifecycle helpers (inactive / reactivate / delete rules)."""
import logging

from django.utils import timezone

from .models import DeliveryAssignment, DriverVehicle, Vehicle

logger = logging.getLogger(__name__)


def vehicle_has_history(vehicle: Vehicle) -> bool:
    """True if the vehicle is linked to assignments or delivery history."""
    return (
        DriverVehicle.objects.filter(vehicle=vehicle).exists()
        or DeliveryAssignment.objects.filter(vehicle=vehicle).exists()
    )


def deactivate_vehicle(vehicle: Vehicle, *, close_assignments: bool = True) -> Vehicle:
    """Mark vehicle inactive and optionally close open driver assignments."""
    if vehicle.active:
        vehicle.active = False
        vehicle.save(update_fields=['active'])

    if close_assignments:
        today = timezone.now().date()
        DriverVehicle.objects.filter(
            vehicle=vehicle,
            assigned_to__isnull=True,
        ).update(assigned_to=today)

    return vehicle


def reactivate_vehicle(vehicle: Vehicle) -> Vehicle:
    """
    Mark vehicle active again.

    Phase 4: enforce insurance/registration reverification before allowing this.
    """
    if not vehicle.active:
        vehicle.active = True
        vehicle.save(update_fields=['active'])
        logger.info(
            'Vehicle %s reactivated; compliance reverification not yet enforced (Phase 4)',
            vehicle.id,
        )
    return vehicle
