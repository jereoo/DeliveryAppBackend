"""Resolve the authenticated user's v1.0 application role."""

from django.contrib.auth.models import User

from .models import Customer, Driver

ROLE_ADMIN = 'admin'
ROLE_CUSTOMER = 'customer'
ROLE_DRIVER = 'driver'


def resolve_current_user_role(user: User) -> dict | None:
    """
    Return role metadata for the current user.

    Priority: staff admin > customer profile > driver profile.
    Returns None when the user has no recognized v1.0 profile.
    """
    if user.is_staff:
        return {
            'role': ROLE_ADMIN,
            'user_id': user.id,
            'profile_id': None,
            'username': user.username,
        }

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
