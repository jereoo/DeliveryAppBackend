"""Tests for GET /api/me/ role resolution."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import Customer, Driver


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
        self._auth(self.admin)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        self.assertEqual(response.data['user_id'], self.admin.id)
        self.assertIsNone(response.data['profile_id'])
        self.assertEqual(response.data['username'], 'adminuser')

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
        Customer.objects.create(
            user=staff_customer_user,
            phone_number='555-0003',
            address_country='US',
        )
        self._auth(staff_customer_user)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        self.assertIsNone(response.data['profile_id'])
