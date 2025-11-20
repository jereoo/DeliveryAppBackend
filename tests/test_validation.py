#!/usr/bin/env python3
"""
Test script to verify postal code validation via API
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class PostalValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.api_url = "/api/customers/register/"

    def test_invalid_canadian_postal_code(self):
        """Test invalid Canadian postal code (US format for CA country)"""
        invalid_ca_data = {
            "username": "invalid.ca.api",
            "email": "invalid.ca.api@test.com",
            "password": "testpass123",
            "first_name": "Invalid",
            "last_name": "Canadian",
            "phone_number": "416-555-1111",
            "address_street": "123 Invalid St",
            "address_city": "Toronto",
            "address_state": "ON",
            "address_postal_code": "12345",  # Invalid for Canada
            "address_country": "CA",
            "is_business": False
        }

        response = self.client.post(self.api_url, invalid_ca_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_postal_code", response.data)

    def test_invalid_us_postal_code(self):
        """Test invalid US postal code (CA format for US country)"""
        invalid_us_data = {
            "username": "invalid.us.api",
            "email": "invalid.us.api@test.com",
            "password": "testpass123",
            "first_name": "Invalid",
            "last_name": "American",
            "phone_number": "555-555-5555",
            "address_street": "456 Invalid Ave",
            "address_city": "New York",
            "address_state": "NY",
            "address_postal_code": "A1A 1A1",  # Invalid for US
            "address_country": "US",
            "is_business": False
        }

        response = self.client.post(self.api_url, invalid_us_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_postal_code", response.data)

    def test_valid_canadian_postal_code(self):
        """Test valid Canadian postal code (K1A 0A6 for CA)"""
        valid_ca_data = {
            "username": "valid.ca.api",
            "email": "valid.ca.api@test.com",
            "password": "testpass123",
            "first_name": "Valid", 
            "last_name": "Canadian",
            "phone_number": "416-555-3333",
            "address_street": "123 Valid St",
            "address_city": "Ottawa",
            "address_state": "ON", 
            "address_postal_code": "K1A 0A6",  # Valid Canadian postal code
            "address_country": "CA",
            "is_business": False
        }
        
        response = self.client.post(self.api_url, valid_ca_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("customer", response.data)
        self.assertEqual(response.data["customer"]["username"], "valid.ca.api")

    def test_valid_us_zip_code(self):
        """Test valid US ZIP code (90210 for US)"""
        valid_us_data = {
            "username": "valid.us.api",
            "email": "valid.us.api@test.com",
            "password": "testpass123",
            "first_name": "Valid",
            "last_name": "American", 
            "phone_number": "555-555-4444",
            "address_street": "123 Valid Ave",
            "address_city": "Beverly Hills",
            "address_state": "CA",
            "address_postal_code": "90210",  # Valid US ZIP code
            "address_country": "US",
            "is_business": False
        }
        
        response = self.client.post(self.api_url, valid_us_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("customer", response.data)
        self.assertEqual(response.data["customer"]["username"], "valid.us.api")