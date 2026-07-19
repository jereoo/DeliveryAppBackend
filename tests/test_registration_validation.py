"""
Registration duplicate-field validation tests (Phase 2).
"""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from delivery.models import Customer, Driver, Vehicle
from delivery.registration_messages import (
    EMAIL_TAKEN,
    LICENSE_NUMBER_TAKEN,
    LICENSE_PLATE_TAKEN,
    USERNAME_TAKEN,
    VIN_TAKEN,
)
from tests.vehicle_catalog_helpers import get_catalog_spec_id


class CustomerRegistrationValidationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.existing_user = User.objects.create_user(
            username='taken_user',
            email='taken@example.com',
            password='testpass123',
        )
        Customer.objects.create(
            user=self.existing_user,
            phone_number='5551111111',
            address_street='1 Main St',
            address_city='Toronto',
            address_state='ON',
            address_postal_code='M5V1A1',
            address_country='CA',
        )
        self.base_payload = {
            'username': 'new_customer',
            'email': 'new@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Customer',
            'phone_number': '5552222222',
            'address_street': '2 Main St',
            'address_city': 'Toronto',
            'address_state': 'ON',
            'address_postal_code': 'M5V2B2',
            'address_country': 'CA',
        }

    def test_duplicate_username_returns_field_error(self):
        payload = {**self.base_payload, 'username': 'taken_user'}
        response = self.client.post('/api/customers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'][0], USERNAME_TAKEN)

    def test_duplicate_email_returns_field_error(self):
        payload = {**self.base_payload, 'email': 'taken@example.com'}
        response = self.client.post('/api/customers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], EMAIL_TAKEN)


class DriverRegistrationValidationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(
            username='driver_taken',
            email='driver_taken@example.com',
            password='testpass123',
            first_name='Taken',
            last_name='Driver',
        )
        Driver.objects.create(
            user=user,
            first_name='Taken',
            last_name='Driver',
            phone_number='5553333333',
            license_number='1111111',
            license_issuing_region='CA-BC',
        )
        Vehicle.objects.create(
            license_plate='PLATE001',
            make='Ford',
            model='Transit',
            year=2020,
            vin='1TAKENTEST0000001',
            capacity=1000,
            capacity_unit='kg',
        )
        self.base_payload = {
            'username': 'new_driver',
            'email': 'newdriver@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'Driver',
            'phone_number': '5554444444',
            'license_issuing_region': 'CA-BC',
            'license_number': '2222222',
            'vehicle_model_spec_id': get_catalog_spec_id(),
            'vehicle_license_plate': 'NEWPLATE1',
            'vehicle_year': 2021,
            'vehicle_vin': '1NEWTEST000000001',
            'vehicle_capacity': 1200,
            'vehicle_capacity_unit': 'kg',
        }

    def test_duplicate_username(self):
        payload = {**self.base_payload, 'username': 'driver_taken'}
        response = self.client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'][0], USERNAME_TAKEN)

    def test_duplicate_email(self):
        payload = {**self.base_payload, 'email': 'driver_taken@example.com'}
        response = self.client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], EMAIL_TAKEN)

    def test_duplicate_license_number(self):
        payload = {**self.base_payload, 'license_number': '1111111'}
        response = self.client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['license_number'][0], LICENSE_NUMBER_TAKEN)

    def test_invalid_license_format(self):
        payload = {**self.base_payload, 'license_number': '12345'}
        response = self.client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('license_number', response.data)

    def test_duplicate_license_plate(self):
        payload = {**self.base_payload, 'vehicle_license_plate': 'PLATE001'}
        response = self.client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['vehicle_license_plate'][0], LICENSE_PLATE_TAKEN)

    def test_duplicate_vin(self):
        payload = {**self.base_payload, 'vehicle_vin': '1TAKENTEST0000001'}
        response = self.client.post('/api/drivers/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['vehicle_vin'][0], VIN_TAKEN)
