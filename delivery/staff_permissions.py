"""Staff permission helpers — single source of truth for role → permission checks."""

from django.contrib.auth.models import User

from .models import StaffProfile
from .staff_constants import PERMISSIONS_BY_ROLE, StaffRole


def get_staff_role_for_user(user: User) -> str:
    """Return staff_role for an is_staff user; default super_admin when profile missing."""
    if not user.is_staff:
        raise ValueError('get_staff_role_for_user requires an is_staff user.')
    try:
        return user.staff_profile.staff_role
    except StaffProfile.DoesNotExist:
        return StaffRole.SUPER_ADMIN


def get_permissions_for_staff_role(staff_role: str) -> list[str]:
    """Sorted permission codes granted to a staff role."""
    return sorted(PERMISSIONS_BY_ROLE.get(staff_role, ()))


def user_has_staff_permission(user: User, permission: str) -> bool:
    """True when user is staff and their role grants the permission code."""
    if not user.is_staff:
        return False
    staff_role = get_staff_role_for_user(user)
    return permission in PERMISSIONS_BY_ROLE.get(staff_role, ())
