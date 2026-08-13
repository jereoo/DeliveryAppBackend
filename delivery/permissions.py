"""v1.0 RBAC permission classes and queryset scoping helpers."""

from rest_framework.permissions import BasePermission

from .driver_utils import get_driver_for_user
from .models import Customer, Delivery, Driver, DriverVehicle
from .staff_constants import (
    PERM_DELIVERIES_ASSIGN,
    PERM_DELIVERIES_VIEW,
    PERM_DRIVERS_APPROVE,
    PERM_DRIVERS_VIEW,
    PERM_REPORTS_VIEW,
    PERM_RESOURCES_VIEW,
    PERM_RESOURCES_WRITE,
)
from .staff_permissions import staff_can_view_operational_data, user_has_staff_permission


def user_has_customer_profile(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return Customer.objects.filter(user=user).exists()


def user_has_driver_profile(user) -> bool:
    return get_driver_for_user(user) is not None


def scope_customer_queryset(user):
    if staff_can_view_operational_data(user):
        return Customer.objects.all()
    return Customer.objects.filter(user=user)


def scope_delivery_queryset(user):
    if staff_can_view_operational_data(user):
        return Delivery.objects.all()
    try:
        customer = user.customer_profile
    except Customer.DoesNotExist:
        return Delivery.objects.none()
    return Delivery.objects.filter(customer=customer)


def scope_driver_queryset(user):
    if staff_can_view_operational_data(user):
        return Driver.objects.all()
    return Driver.objects.filter(user=user)


def scope_driver_vehicle_queryset(user):
    if staff_can_view_operational_data(user):
        return DriverVehicle.objects.all()
    driver = get_driver_for_user(user)
    if not driver:
        return DriverVehicle.objects.none()
    return DriverVehicle.objects.filter(driver=driver)


class IsStaffUser(BasePermission):
    """Staff with compliance/report read access (inbox, summaries)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and user_has_staff_permission(request.user, PERM_REPORTS_VIEW)
        )


class CanManageCustomer(BasePermission):
    """Staff manage all customers; customers read/update own profile only."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if view.action in ('create', 'destroy'):
            return user_has_staff_permission(request.user, PERM_RESOURCES_WRITE)
        return True

    def has_object_permission(self, request, view, obj):
        if user_has_staff_permission(request.user, PERM_RESOURCES_WRITE):
            return True
        if user_has_staff_permission(request.user, PERM_RESOURCES_VIEW):
            return view.action in ('retrieve', 'list')
        if view.action in ('retrieve', 'update', 'partial_update'):
            return obj.user_id == request.user.id
        return False


class CanManageDelivery(BasePermission):
    """Staff CRUD; customers list/read own deliveries and use request_delivery."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if view.action in ('create', 'destroy'):
            return user_has_staff_permission(request.user, PERM_RESOURCES_WRITE)
        if view.action == 'request_delivery':
            return user_has_customer_profile(request.user)
        if view.action == 'cancel':
            return (
                user_has_staff_permission(request.user, PERM_RESOURCES_WRITE)
                or user_has_customer_profile(request.user)
            )
        return True

    def has_object_permission(self, request, view, obj):
        if user_has_staff_permission(request.user, PERM_RESOURCES_WRITE):
            return True
        if user_has_staff_permission(request.user, PERM_DELIVERIES_VIEW):
            return view.action in ('retrieve', 'list')
        if view.action in ('retrieve', 'cancel'):
            try:
                return obj.customer_id == request.user.customer_profile.id
            except Customer.DoesNotExist:
                return False
        return False


class CanManageDriver(BasePermission):
    """Staff create/delete/approve; drivers read/update own profile."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if view.action in ('create', 'destroy'):
            return user_has_staff_permission(request.user, PERM_RESOURCES_WRITE)
        if view.action in ('approve', 'reject'):
            return user_has_staff_permission(request.user, PERM_DRIVERS_APPROVE)
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ('approve', 'reject'):
            return user_has_staff_permission(request.user, PERM_DRIVERS_APPROVE)
        if user_has_staff_permission(request.user, PERM_RESOURCES_WRITE):
            return True
        if user_has_staff_permission(request.user, PERM_DRIVERS_VIEW):
            return view.action in ('retrieve', 'list', 'dispatch_eligibility')
        if view.action in ('retrieve', 'update', 'partial_update', 'assign_vehicle'):
            return obj.user_id == request.user.id
        return False


class CanManageDriverVehicleAssignment(BasePermission):
    """Staff manage assignment history; drivers read own rows."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if view.action in ('create', 'update', 'partial_update', 'destroy'):
            return user_has_staff_permission(request.user, PERM_RESOURCES_WRITE)
        return True

    def has_object_permission(self, request, view, obj):
        if user_has_staff_permission(request.user, PERM_RESOURCES_WRITE):
            return True
        if user_has_staff_permission(request.user, PERM_DRIVERS_VIEW):
            return view.action in ('retrieve', 'list')
        if view.action in ('retrieve',):
            driver = get_driver_for_user(request.user)
            return driver is not None and obj.driver_id == driver.id
        return False


class CanManageDeliveryAssignment(BasePermission):
    """Dispatch assignments require deliveries.assign to mutate."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if view.action in ('create', 'update', 'partial_update', 'destroy'):
            return user_has_staff_permission(request.user, PERM_DELIVERIES_ASSIGN)
        if view.action in ('list', 'retrieve'):
            return (
                user_has_staff_permission(request.user, PERM_DELIVERIES_VIEW)
                or user_has_driver_profile(request.user)
                or user_has_customer_profile(request.user)
            )
        return True
