"""Tests for v1.0 permission classes and queryset scoping (Phase B)."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from delivery.models import Customer, Driver, DriverVehicle, Vehicle


class PermissionScopingTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='permadmin',
            email='permadmin@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.customer_user = User.objects.create_user(
            username='permcustomer',
            email='permcustomer@example.com',
            password='testpass123',
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            phone_number='5551001',
            address_country='US',
        )
        self.driver_user = User.objects.create_user(
            username='permdriver',
            email='permdriver@example.com',
            password='testpass123',
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            phone_number='5551002',
            license_number='PERMDL001',
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='PERM01',
            make='Ford',
            model='Transit',
            year=2022,
            vin='1PERMTESTVIN00001',
            capacity=1500,
            capacity_unit='kg',
        )
        self.other_driver_user = User.objects.create_user(
            username='permotherdriver',
            email='permother@example.com',
            password='testpass123',
        )
        self.other_driver = Driver.objects.create(
            user=self.other_driver_user,
            phone_number='5551003',
            license_number='PERMDL002',
            first_name='Other',
            last_name='Driver',
        )
        self.driver_assignment = DriverVehicle.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            assigned_from='2026-01-01',
        )
        self.other_assignment = DriverVehicle.objects.create(
            driver=self.other_driver,
            vehicle=self.vehicle,
            assigned_from='2026-02-01',
            assigned_to='2026-06-01',
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_customer_cannot_create_customer_via_admin_endpoint(self):
        self._auth(self.customer_user)
        response = self.client.post('/api/customers/', {
            'username': 'blocked',
            'email': 'blocked@example.com',
            'password': 'testpass123',
            'first_name': 'Blocked',
            'last_name': 'User',
            'phone_number': '5559999999',
            'address_country': 'US',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_driver_sees_only_own_driver_vehicle_rows(self):
        self._auth(self.driver_user)
        response = self.client.get('/api/driver-vehicles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row['id'] for row in response.data['results']]
        self.assertEqual(ids, [self.driver_assignment.id])

    def test_admin_sees_all_driver_vehicle_rows(self):
        self._auth(self.admin)
        response = self.client.get('/api/driver-vehicles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row['id'] for row in response.data['results']}
        self.assertIn(self.driver_assignment.id, ids)
        self.assertIn(self.other_assignment.id, ids)

    def test_driver_cannot_create_driver_vehicle_assignment(self):
        self._auth(self.driver_user)
        response = self.client.post('/api/driver-vehicles/', {
            'driver': self.driver.id,
            'vehicle': self.vehicle.id,
            'assigned_from': '2026-07-01',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_gets_empty_driver_vehicle_list(self):
        self._auth(self.customer_user)
        response = self.client.get('/api/driver-vehicles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_driver_cannot_create_delivery_assignment(self):
        self._auth(self.driver_user)
        response = self.client.post('/api/assignments/', {
            'delivery': 1,
            'driver': self.driver.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
