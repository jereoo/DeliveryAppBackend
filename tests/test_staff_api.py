"""Tests for Phase 4G staff user admin API."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import StaffProfile
from delivery.staff_constants import StaffRole


class StaffUserApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.super_admin = User.objects.create_user(
            username='superadmin',
            password='testpass123',
            email='super@example.com',
            is_staff=True,
            is_superuser=True,
        )
        StaffProfile.objects.create(
            user=self.super_admin,
            staff_role=StaffRole.SUPER_ADMIN,
        )
        self.ops_admin = User.objects.create_user(
            username='opsadmin',
            password='testpass123',
            email='ops@example.com',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=self.ops_admin,
            staff_role=StaffRole.OPERATIONS_ADMIN,
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_super_admin_can_list_staff(self):
        self._auth(self.super_admin)
        response = self.client.get('/api/staff/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {row['username'] for row in response.data}
        self.assertIn('superadmin', usernames)
        self.assertIn('opsadmin', usernames)

    def test_operations_admin_cannot_list_staff(self):
        self._auth(self.ops_admin)
        response = self.client.get('/api/staff/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_create_staff_user(self):
        self._auth(self.super_admin)
        response = self.client.post(
            '/api/staff/',
            {
                'username': 'reviewer1',
                'email': 'reviewer1@example.com',
                'password': 'SecurePass1!',
                'first_name': 'Comp',
                'last_name': 'Reviewer',
                'staff_role': StaffRole.COMPLIANCE_REVIEWER,
                'job_title': 'Compliance',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['staff_role'], StaffRole.COMPLIANCE_REVIEWER)
        self.assertEqual(response.data['role'] if 'role' in response.data else None, None)
        profile = StaffProfile.objects.get(user__username='reviewer1')
        self.assertFalse(profile.user.is_superuser)
        self.assertTrue(profile.user.is_staff)

        self.client.credentials()
        self._auth(profile.user)
        me = self.client.get('/api/me/')
        self.assertEqual(me.data['role'], 'staff')
        self.assertEqual(me.data['staff_role'], StaffRole.COMPLIANCE_REVIEWER)

    def test_operations_admin_cannot_create_staff(self):
        self._auth(self.ops_admin)
        response = self.client.post(
            '/api/staff/',
            {
                'username': 'blocked',
                'email': 'blocked@example.com',
                'password': 'SecurePass1!',
                'first_name': 'No',
                'last_name': 'Access',
                'staff_role': StaffRole.READ_ONLY,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_update_staff_role(self):
        target = User.objects.create_user(
            username='targetstaff',
            password='testpass123',
            email='target@example.com',
            is_staff=True,
        )
        profile = StaffProfile.objects.create(
            user=target,
            staff_role=StaffRole.READ_ONLY,
        )
        self._auth(self.super_admin)
        response = self.client.patch(
            f'/api/staff/{profile.id}/',
            {'staff_role': StaffRole.OPERATIONS_ADMIN},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(profile.staff_role, StaffRole.OPERATIONS_ADMIN)

    def test_super_admin_can_deactivate_staff(self):
        target = User.objects.create_user(
            username='deactivateme',
            password='testpass123',
            email='deactivate@example.com',
            is_staff=True,
        )
        profile = StaffProfile.objects.create(
            user=target,
            staff_role=StaffRole.READ_ONLY,
        )
        self._auth(self.super_admin)
        response = self.client.patch(
            f'/api/staff/{profile.id}/',
            {'is_active': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertFalse(target.is_active)

    def test_super_admin_cannot_deactivate_self(self):
        profile = self.super_admin.staff_profile
        self._auth(self.super_admin)
        response = self.client.patch(
            f'/api/staff/{profile.id}/',
            {'is_active': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.super_admin.refresh_from_db()
        self.assertTrue(self.super_admin.is_active)

    def test_cannot_demote_last_super_admin(self):
        profile = self.super_admin.staff_profile
        self._auth(self.super_admin)
        response = self.client.patch(
            f'/api/staff/{profile.id}/',
            {'staff_role': StaffRole.OPERATIONS_ADMIN},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_search_filter(self):
        self._auth(self.super_admin)
        response = self.client.get('/api/staff/', {'search': 'ops@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'opsadmin')
