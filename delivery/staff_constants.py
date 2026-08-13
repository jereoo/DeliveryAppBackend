"""Staff role and permission constants for Phase 4G RBAC (v1.0 single-fleet)."""

from django.db import models


class StaffRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    OPERATIONS_ADMIN = 'operations_admin', 'Operations Admin'
    COMPLIANCE_REVIEWER = 'compliance_reviewer', 'Compliance Reviewer'
    READ_ONLY = 'read_only', 'Read Only'


# Permission codes — enforced on API in Phase 4G slice 3+.
PERM_STAFF_MANAGE = 'staff.manage'
PERM_DRIVERS_APPROVE = 'drivers.approve'
PERM_DRIVERS_VIEW = 'drivers.view'
PERM_COMPLIANCE_VERIFY = 'compliance.verify'
PERM_COMPLIANCE_VIEW = 'compliance.view'
PERM_DELIVERIES_ASSIGN = 'deliveries.assign'
PERM_DELIVERIES_VIEW = 'deliveries.view'
PERM_RESOURCES_WRITE = 'resources.write'
PERM_RESOURCES_VIEW = 'resources.view'
PERM_VEHICLES_REACTIVATE = 'vehicles.reactivate'
PERM_VEHICLES_VIEW = 'vehicles.view'
PERM_REPORTS_VIEW = 'reports.view'

VIEW_PERMISSIONS = (
    PERM_DRIVERS_VIEW,
    PERM_COMPLIANCE_VIEW,
    PERM_DELIVERIES_VIEW,
    PERM_RESOURCES_VIEW,
    PERM_VEHICLES_VIEW,
    PERM_REPORTS_VIEW,
)

ALL_STAFF_PERMISSIONS = (
    PERM_STAFF_MANAGE,
    PERM_DRIVERS_APPROVE,
    PERM_COMPLIANCE_VERIFY,
    PERM_DELIVERIES_ASSIGN,
    PERM_RESOURCES_WRITE,
    PERM_VEHICLES_REACTIVATE,
    *VIEW_PERMISSIONS,
)

# Role → permission matrix (PROJECT_PLAN Phase 4G).
PERMISSIONS_BY_ROLE: dict[str, frozenset[str]] = {
    StaffRole.SUPER_ADMIN: frozenset(ALL_STAFF_PERMISSIONS),
    StaffRole.OPERATIONS_ADMIN: frozenset(
        {
            PERM_DRIVERS_APPROVE,
            PERM_COMPLIANCE_VERIFY,
            PERM_DELIVERIES_ASSIGN,
            PERM_RESOURCES_WRITE,
            PERM_VEHICLES_REACTIVATE,
            *VIEW_PERMISSIONS,
        }
    ),
    StaffRole.COMPLIANCE_REVIEWER: frozenset(
        {
            PERM_COMPLIANCE_VERIFY,
            *VIEW_PERMISSIONS,
        }
    ),
    StaffRole.READ_ONLY: frozenset(VIEW_PERMISSIONS),
}
