"""Tests for GET /api/me/ role resolution."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import Customer, Driver, StaffProfile
from delivery.staff_constants import PERM_COMPLIANCE_VERIFY, PERM_STAFF_MANAGE, StaffRole


class CurrentUserMeTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.customer_user = User.objects.create_user(
            username='customeruser',
            email='customer@example.com',
            password='testpass123',
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            phone_number='555-0001',
            address_country='US',
        )
        self.driver_user = User.objects.create_user(
            username='driveruser',
            email='driver@example.com',
            password='testpass123',
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            phone_number='555-0002',
            license_number='DL123456',
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_me_requires_authentication(self):
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_admin_for_staff(self):
        StaffProfile.objects.create(
            user=self.admin,
            staff_role=StaffRole.SUPER_ADMIN,
        )
        self._auth(self.admin)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        self.assertEqual(response.data['staff_role'], StaffRole.SUPER_ADMIN)
        self.assertIn(PERM_STAFF_MANAGE, response.data['permissions'])
        self.assertEqual(response.data['user_id'], self.admin.id)
        self.assertEqual(response.data['profile_id'], self.admin.staff_profile.id)
        self.assertEqual(response.data['username'], 'adminuser')

    def test_me_returns_staff_for_operations_admin(self):
        ops_user = User.objects.create_user(
            username='opsuser',
            email='ops@example.com',
            password='testpass123',
            is_staff=True,
        )
        profile = StaffProfile.objects.create(
            user=ops_user,
            staff_role=StaffRole.OPERATIONS_ADMIN,
        )
        self._auth(ops_user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'staff')
        self.assertEqual(response.data['staff_role'], StaffRole.OPERATIONS_ADMIN)
        self.assertNotIn(PERM_STAFF_MANAGE, response.data['permissions'])
        self.assertIn(PERM_COMPLIANCE_VERIFY, response.data['permissions'])
        self.assertEqual(response.data['profile_id'], profile.id)

    def test_me_returns_staff_for_compliance_reviewer(self):
        reviewer = User.objects.create_user(
            username='compreviewer',
            email='comp@example.com',
            password='testpass123',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=reviewer,
            staff_role=StaffRole.COMPLIANCE_REVIEWER,
        )
        self._auth(reviewer)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'staff')
        self.assertEqual(response.data['staff_role'], StaffRole.COMPLIANCE_REVIEWER)
        self.assertIn(PERM_COMPLIANCE_VERIFY, response.data['permissions'])
        self.assertNotIn(PERM_STAFF_MANAGE, response.data['permissions'])

    def test_me_returns_staff_for_read_only(self):
        viewer = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='testpass123',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=viewer,
            staff_role=StaffRole.READ_ONLY,
        )
        self._auth(viewer)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'staff')
        self.assertTrue(all(p.endswith('.view') for p in response.data['permissions']))

    def test_me_returns_customer_profile(self):
        self._auth(self.customer_user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'customer')
        self.assertEqual(response.data['user_id'], self.customer_user.id)
        self.assertEqual(response.data['profile_id'], self.customer.id)
        self.assertEqual(response.data['username'], 'customeruser')

    def test_me_returns_driver_profile(self):
        self._auth(self.driver_user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'driver')
        self.assertEqual(response.data['user_id'], self.driver_user.id)
        self.assertEqual(response.data['profile_id'], self.driver.id)
        self.assertEqual(response.data['username'], 'driveruser')

    def test_me_returns_403_without_profile(self):
        plain_user = User.objects.create_user(
            username='plainuser',
            email='plain@example.com',
            password='testpass123',
        )
        self._auth(plain_user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_role_takes_priority_over_customer_profile(self):
        staff_customer_user = User.objects.create_user(
            username='staffcustomer',
            email='staffcustomer@example.com',
            password='testpass123',
            is_staff=True,
        )
        StaffProfile.objects.create(
            user=staff_customer_user,
            staff_role=StaffRole.SUPER_ADMIN,
        )
        Customer.objects.create(
            user=staff_customer_user,
            phone_number='555-0003',
            address_country='US',
        )
        self._auth(staff_customer_user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        self.assertEqual(response.data['profile_id'], staff_customer_user.staff_profile.id)
