"""Staff permission helpers — single source of truth for role → permission checks."""

from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from .models import StaffProfile
from .staff_constants import (
    PERMISSIONS_BY_ROLE,
    PERM_COMPLIANCE_VIEW,
    PERM_COMPLIANCE_VERIFY,
    PERM_DELIVERIES_ASSIGN,
    PERM_DELIVERIES_VIEW,
    PERM_DRIVERS_APPROVE,
    PERM_DRIVERS_VIEW,
    PERM_REPORTS_VIEW,
    PERM_RESOURCES_VIEW,
    PERM_RESOURCES_WRITE,
    PERM_STAFF_MANAGE,
    PERM_VEHICLES_REACTIVATE,
    PERM_VEHICLES_VIEW,
    VIEW_PERMISSIONS,
    StaffRole,
)


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


def staff_can_view_operational_data(user: User) -> bool:
    """Staff with any read permission (all v1.0 staff roles)."""
    if not user.is_staff:
        return False
    return any(user_has_staff_permission(user, perm) for perm in VIEW_PERMISSIONS)


def require_staff_permission(user: User, permission: str, *, message: str | None = None) -> None:
    if not user_has_staff_permission(user, permission):
        raise PermissionDenied(message or 'You do not have permission for this action.')


class CanManageStaffUsers(BasePermission):
    """Super Admin only — staff.manage permission."""

    def has_permission(self, request, view):
        return user_has_staff_permission(request.user, PERM_STAFF_MANAGE)
