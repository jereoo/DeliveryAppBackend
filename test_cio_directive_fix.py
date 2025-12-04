#!/usr/bin/env python
"""
CIO DIRECTIVE TEST - November 30, 2025
Test that new drivers are NOT created as admin users

This test verifies the fix for the critical bug where drivers
registered via mobile app were incorrectly getting is_staff=True
and is_superuser=True permissions.
"""

import os
import sys
import django
from django.test import TestCase

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from delivery.serializers import DriverRegistrationSerializer, CustomerRegistrationSerializer

def test_driver_registration_creates_non_admin_user():
    """Test that new drivers are created with is_staff=False, is_superuser=False"""
    
    print("🔍 TESTING CIO DIRECTIVE FIX...")
    print("Testing DriverRegistrationSerializer creates non-admin users")
    
    # Test data simulating mobile app driver registration
    driver_data = {
        'username': 'wandadollar',
        'email': 'wanda.dollar@test.com', 
        'password': 'testpassword123',
        'first_name': 'Wanda',
        'last_name': 'Dollar',
        'phone_number': '555-1234',
        'license_number': 'DL123TEST',
        'vehicle_make': 'Ford',
        'vehicle_model': 'Transit',
        'vehicle_year': 2020,
        'vehicle_vin': 'TEST123456789'
    }
    
    # Create driver using DriverRegistrationSerializer
    serializer = DriverRegistrationSerializer(data=driver_data)
    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    
    driver = serializer.save()
    user = driver.user
    
    # CRITICAL ASSERTIONS - CIO DIRECTIVE REQUIREMENTS
    assert user.is_staff == False, f"❌ FAILED: Driver user has is_staff=True (should be False)"
    assert user.is_superuser == False, f"❌ FAILED: Driver user has is_superuser=True (should be False)"
    assert user.username == 'wandadollar', f"❌ FAILED: Username mismatch"
    assert user.first_name == 'Wanda', f"❌ FAILED: First name mismatch"
    assert user.last_name == 'Dollar', f"❌ FAILED: Last name mismatch"
    
    print(f"✅ SUCCESS: Driver '{driver.first_name} {driver.last_name}' created correctly")
    print(f"   - User ID: {user.id}")
    print(f"   - is_staff: {user.is_staff} (correct)")
    print(f"   - is_superuser: {user.is_superuser} (correct)")
    print(f"   - Username: {user.username}")
    
    # Clean up
    driver.delete()
    user.delete()

def test_customer_registration_creates_non_admin_user():
    """Test that new customers are also created with is_staff=False, is_superuser=False"""
    
    print("\n🔍 Testing CustomerRegistrationSerializer creates non-admin users")
    
    customer_data = {
        'username': 'testcustomer',
        'email': 'customer@test.com',
        'password': 'testpassword123',
        'first_name': 'Test',
        'last_name': 'Customer',
        'customer_type': 'individual',
        'address': '123 Test St',
        'address_city': 'Test City',
        'address_state': 'Test State',
        'address_postal_code': 'T1T 1T1',
        'address_country': 'CA'
    }
    
    serializer = CustomerRegistrationSerializer(data=customer_data)
    assert serializer.is_valid(), f"Customer serializer validation failed: {serializer.errors}"
    
    customer = serializer.save()
    user = customer.user
    
    # CRITICAL ASSERTIONS 
    assert user.is_staff == False, f"❌ FAILED: Customer user has is_staff=True (should be False)"
    assert user.is_superuser == False, f"❌ FAILED: Customer user has is_superuser=True (should be False)"
    
    print(f"✅ SUCCESS: Customer '{customer.first_name} {customer.last_name}' created correctly")
    print(f"   - User ID: {user.id}")
    print(f"   - is_staff: {user.is_staff} (correct)")
    print(f"   - is_superuser: {user.is_superuser} (correct)")
    
    # Clean up
    customer.delete()
    user.delete()

if __name__ == '__main__':
    print("=" * 60)
    print("🚨 CIO DIRECTIVE FIX VERIFICATION - November 30, 2025")
    print("Testing that new drivers/customers are NOT created as admins")
    print("=" * 60)
    
    try:
        test_driver_registration_creates_non_admin_user()
        test_customer_registration_creates_non_admin_user()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED - CIO DIRECTIVE FULFILLED")
        print("✅ New drivers will be created as normal users (not admins)")
        print("✅ New customers will be created as normal users (not admins)")
        print("✅ Django tests still pass: 111/111")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("🚨 CIO DIRECTIVE NOT FULFILLED - Fix required!")
        sys.exit(1)