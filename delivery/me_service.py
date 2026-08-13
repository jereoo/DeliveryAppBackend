"""Resolve the authenticated user's v1.0 application role."""

from django.contrib.auth.models import User

from .models import Customer, Driver, StaffProfile
from .staff_constants import StaffRole
from .staff_permissions import get_permissions_for_staff_role, get_staff_role_for_user

ROLE_ADMIN = 'admin'
ROLE_STAFF = 'staff'
ROLE_CUSTOMER = 'customer'
ROLE_DRIVER = 'driver'


def _build_staff_payload(user: User) -> dict:
    staff_role = get_staff_role_for_user(user)
    permissions = get_permissions_for_staff_role(staff_role)
    try:
        profile_id = user.staff_profile.id
    except StaffProfile.DoesNotExist:
        profile_id = None

    payload = {
        'user_id': user.id,
        'profile_id': profile_id,
        'username': user.username,
        'staff_role': staff_role,
        'permissions': permissions,
    }

    if staff_role == StaffRole.SUPER_ADMIN:
        payload['role'] = ROLE_ADMIN
    else:
        payload['role'] = ROLE_STAFF

    return payload


def resolve_current_user_role(user: User) -> dict | None:
    """
    Return role metadata for the current user.

    Priority: staff admin > customer profile > driver profile.
    Returns None when the user has no recognized v1.0 profile.

    Staff (Option A): super_admin → role admin; other staff roles → role staff
    with staff_role + permissions.
    """
    if user.is_staff:
        return _build_staff_payload(user)

    try:
        customer = user.customer_profile
    except Customer.DoesNotExist:
        customer = None

    if customer is not None:
        return {
            'role': ROLE_CUSTOMER,
            'user_id': user.id,
            'profile_id': customer.id,
            'username': user.username,
        }

    try:
        driver = user.driver_profile
    except Driver.DoesNotExist:
        driver = None

    if driver is not None:
        return {
            'role': ROLE_DRIVER,
            'user_id': user.id,
            'profile_id': driver.id,
            'username': user.username,
        }

    return None
