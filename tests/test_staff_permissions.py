"""Tests for staff role permission helpers."""

from django.contrib.auth.models import User
from django.test import TestCase

from delivery.models import StaffProfile
from delivery.staff_constants import (
    PERM_COMPLIANCE_VERIFY,
    PERM_DELIVERIES_ASSIGN,
    PERM_RESOURCES_WRITE,
    PERM_STAFF_MANAGE,
    StaffRole,
)
from delivery.staff_permissions import (
    get_permissions_for_staff_role,
    get_staff_role_for_user,
    user_has_staff_permission,
)


class StaffPermissionTests(TestCase):
    def setUp(self):
        self.super_admin = User.objects.create_user(
            username='superadmin',
            password='testpass123',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=self.super_admin,
            staff_role=StaffRole.SUPER_ADMIN,
        )
        self.ops_admin = User.objects.create_user(
            username='opsadmin',
            password='testpass123',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=self.ops_admin,
            staff_role=StaffRole.OPERATIONS_ADMIN,
        )
        self.reviewer = User.objects.create_user(
            username='reviewer',
            password='testpass123',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=self.reviewer,
            staff_role=StaffRole.COMPLIANCE_REVIEWER,
        )
        self.read_only = User.objects.create_user(
            username='readonly',
            password='testpass123',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=self.read_only,
            staff_role=StaffRole.READ_ONLY,
        )

    def test_super_admin_has_staff_manage(self):
        self.assertTrue(user_has_staff_permission(self.super_admin, PERM_STAFF_MANAGE))

    def test_operations_admin_cannot_manage_staff(self):
        self.assertFalse(user_has_staff_permission(self.ops_admin, PERM_STAFF_MANAGE))
        self.assertTrue(user_has_staff_permission(self.ops_admin, PERM_DELIVERIES_ASSIGN))

    def test_compliance_reviewer_can_verify_not_assign(self):
        self.assertTrue(user_has_staff_permission(self.reviewer, PERM_COMPLIANCE_VERIFY))
        self.assertFalse(user_has_staff_permission(self.reviewer, PERM_DELIVERIES_ASSIGN))

    def test_read_only_has_view_permissions_only(self):
        perms = get_permissions_for_staff_role(StaffRole.READ_ONLY)
        self.assertTrue(all(p.endswith('.view') for p in perms))
        self.assertFalse(user_has_staff_permission(self.read_only, PERM_RESOURCES_WRITE))

    def test_legacy_staff_without_profile_defaults_super_admin(self):
        legacy = User.objects.create_user(
            username='legacyadmin',
            password='testpass123',
            is_staff=True,
        )
        self.assertEqual(get_staff_role_for_user(legacy), StaffRole.SUPER_ADMIN)
