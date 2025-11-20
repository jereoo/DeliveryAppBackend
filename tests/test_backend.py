from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class BackendTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_registration_url = "/api/customers/register/"
        self.delivery_request_url = "/api/deliveries/request_delivery/"

    def test_customer_registration(self):
        """Test customer registration with valid data"""
        valid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "555-1234",
            "address_street": "123 Test St",
            "address_city": "Test City",
            "address_state": "Test State",
            "address_postal_code": "12345",
            "address_country": "US"
        }

        response = self.client.post(self.customer_registration_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("customer", response.data)
        self.assertEqual(response.data["customer"]["username"], "testuser")

    def test_delivery_request_without_authentication(self):
        """Test delivery request without authentication"""
        delivery_data = {
            "pickup_location": "123 Test St",
            "dropoff_location": "456 Destination Ave",
            "item_description": "Test Package"
        }

        response = self.client.post(self.delivery_request_url, delivery_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delivery_request_with_authentication(self):
        """Test delivery request with authentication"""
        # Register a customer
        customer_data = {
            "username": "authuser",
            "email": "authuser@example.com",
            "password": "authpass123",
            "first_name": "Auth",
            "last_name": "User",
            "phone_number": "555-5678",
            "address_street": "456 Auth St",
            "address_city": "Auth City",
            "address_state": "Auth State",
            "address_postal_code": "67890",
            "address_country": "US"
        }
        self.client.post(self.customer_registration_url, customer_data, format='json')

        # Authenticate the customer
        auth_response = self.client.post("/api/token/", {
            "username": "authuser",
            "password": "authpass123"
        }, format='json')
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
        token = auth_response.data["access"]

        # Make an authenticated delivery request
        delivery_data = {
            "pickup_location": "456 Auth St",
            "dropoff_location": "789 Delivery Ave",
            "item_description": "Authenticated Package"
        }
        response = self.client.post(
            self.delivery_request_url,
            delivery_data,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("delivery", response.data)
        self.assertIn("id", response.data["delivery"])