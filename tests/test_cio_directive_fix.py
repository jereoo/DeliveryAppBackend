"""
CIO DIRECTIVE TEST - November 30, 2025
Test that new drivers are NOT created as admin users

This test verifies the fix for the critical bug where drivers
registered via mobile app were incorrectly getting is_staff=True
and is_superuser=True permissions.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from delivery.serializers import DriverRegistrationSerializer, CustomerRegistrationSerializer
from delivery.models import Driver, Customer, Vehicle
from tests.vehicle_catalog_helpers import get_catalog_spec_id


class CIODirectiveFixTests(TestCase):
    """Test that CIO directive is fulfilled - no admin drivers created"""

    def test_driver_registration_creates_non_admin_user(self):
        """Test that new drivers are created with is_staff=False, is_superuser=False"""
        
        # Test data simulating mobile app driver registration (like "wanda dollar")
        driver_data = {
            'username': 'wandadollar',
            'email': 'wanda.dollar@test.com', 
            'password': 'testpassword123',
            'first_name': 'Wanda',
            'last_name': 'Dollar',
            'phone_number': '5551234567',
            'license_issuing_region': 'CA-BC',
            'license_number': '5555555',
            'vehicle_model_spec_id': get_catalog_spec_id(),
            'vehicle_license_plate': 'ABC123',
            'vehicle_year': 2020,
            'vehicle_vin': 'TEST1234567890123',  # 17 characters required
            'vehicle_capacity': 1000,
            'vehicle_capacity_unit': 'kg'
        }
        
        # Create driver using DriverRegistrationSerializer
        serializer = DriverRegistrationSerializer(data=driver_data)
        self.assertTrue(serializer.is_valid(), f"Serializer validation failed: {serializer.errors}")
        
        driver = serializer.save()
        user = driver.user
        
        # CRITICAL ASSERTIONS - CIO DIRECTIVE REQUIREMENTS
        self.assertFalse(user.is_staff, "❌ FAILED: Driver user has is_staff=True (should be False)")
        self.assertFalse(user.is_superuser, "❌ FAILED: Driver user has is_superuser=True (should be False)")
        self.assertEqual(user.username, 'wandadollar')
        self.assertEqual(user.first_name, 'Wanda')
        self.assertEqual(user.last_name, 'Dollar')
        
        # Verify driver fields are properly set
        self.assertEqual(driver.first_name, 'Wanda')
        self.assertEqual(driver.last_name, 'Dollar')
        self.assertEqual(driver.phone_number, '5551234567')
        self.assertEqual(driver.license_number, '5555555')
        vehicle = driver.drivervehicle_set.first().vehicle
        self.assertEqual(vehicle.make, 'Ford')
        self.assertEqual(vehicle.model, 'F-150')
        
        print(f"SUCCESS: Driver '{driver.first_name} {driver.last_name}' created correctly")
        print(f"   - User ID: {user.id}")
        print(f"   - is_staff: {user.is_staff} (correct - False)")
        print(f"   - is_superuser: {user.is_superuser} (correct - False)")

    def test_customer_registration_creates_non_admin_user(self):
        """Test that new customers are also created with is_staff=False, is_superuser=False"""
        
        customer_data = {
            'username': 'testcustomer',
            'email': 'customer@test.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'Customer',
            'phone_number': '5555678901',
            'address_street': '123 Test St',
            'address_city': 'Test City',
            'address_state': 'ON',
            'address_postal_code': 'K1A 0A6',
            'address_country': 'CA',
            'is_business': False,
        }
        
        serializer = CustomerRegistrationSerializer(data=customer_data)
        self.assertTrue(serializer.is_valid(), f"Customer serializer validation failed: {serializer.errors}")
        
        customer = serializer.save()
        user = customer.user
        
        # CRITICAL ASSERTIONS 
        self.assertFalse(user.is_staff, "❌ FAILED: Customer user has is_staff=True (should be False)")
        self.assertFalse(user.is_superuser, "❌ FAILED: Customer user has is_superuser=True (should be False)")
        
        print(f"SUCCESS: Customer '{user.first_name} {user.last_name}' created correctly")
        print(f"   - User ID: {user.id}")
        print(f"   - is_staff: {user.is_staff} (correct - False)")
        print(f"   - is_superuser: {user.is_superuser} (correct - False)")

    def test_manual_driver_creation_with_user_still_works(self):
        """Test that manual driver creation (via model) still works with user field."""

        user = User.objects.create_user(
            username='manualdriver',
            first_name='Manual',
            last_name='Driver',
            email='manual@test.com',
            password='testpass123',
            is_staff=False,
            is_superuser=False,
        )

        driver = Driver.objects.create(
            user=user,
            first_name='Manual',
            last_name='Driver',
            phone_number='5559999999',
            license_number='DL999MANUAL',
            active=True,
        )

        self.assertEqual(driver.user, user)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        print("SUCCESS: Manual driver creation still works")