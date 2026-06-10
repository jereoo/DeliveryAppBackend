"""Auth and registration failure logging tests."""
from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class AuthLoggingTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='known_user', password='correctpass123')
        self.client = APIClient()

    @patch('delivery.views_auth.log_jwt_login_failure')
    def test_failed_jwt_login_is_logged(self, mock_log):
        response = self.client.post('/api/token/', {
            'username': 'known_user',
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_log.assert_called_once()

    @patch('delivery.views.log_registration_validation_failure')
    def test_driver_registration_failure_is_logged(self, mock_log):
        User.objects.create_user(username='dup', email='dup@example.com', password='testpass123')
        response = self.client.post('/api/drivers/register/', {
            'username': 'dup',
            'email': 'other@example.com',
            'password': 'testpass123',
            'first_name': 'A',
            'last_name': 'B',
            'phone_number': '5555555555',
            'license_number': 'DL-X',
            'vehicle_license_plate': 'X1',
            'vehicle_make': 'Ford',
            'vehicle_model': 'Transit',
            'vehicle_year': 2020,
            'vehicle_vin': '1LOGTEST000000001',
            'vehicle_capacity': 1000,
            'vehicle_capacity_unit': 'kg',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_log.assert_called_once()

    def test_request_id_header_on_response(self):
        response = self.client.get('/api/health/')
        self.assertIn('X-Request-ID', response)
