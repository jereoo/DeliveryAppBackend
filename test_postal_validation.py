#!/usr/bin/env python3
"""
Test script to verify postal code validation via API
"""

import requests
import json

def test_postal_validation():
    print("🧪 TESTING POSTAL CODE VALIDATION VIA API")
    print("=" * 50)
    
    api_url = "http://localhost:8081/api/customers/register/"
    headers = {"Content-Type": "application/json"}
    
    # Test 1: Invalid Canadian postal code (US format for CA country)
    print("Test 1: Invalid Canadian postal code (12345 for CA)")
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
    
    try:
        response = requests.post(api_url, json=invalid_ca_data, headers=headers)
        if response.status_code == 400:
            print("✅ VALIDATION WORKING: HTTP 400 Bad Request")
            print(f"   Error details: {response.json()}")
        elif response.status_code == 201:
            print("❌ ERROR: Customer created when validation should have failed")
            print(f"   Created customer: {response.json().get('username')}")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()
    
    # Test 2: Invalid US postal code (CA format for US country)  
    print("Test 2: Invalid US postal code (A1A 1A1 for US)")
    invalid_us_data = {
        "username": "invalid.us.api",
        "email": "invalid.us.api@test.com",
        "password": "testpass123", 
        "first_name": "Invalid",
        "last_name": "American",
        "phone_number": "555-555-2222",
        "address_street": "123 Invalid Ave",
        "address_city": "Springfield",
        "address_state": "IL",
        "address_postal_code": "A1A 1A1",  # Invalid for US
        "address_country": "US",
        "is_business": False
    }
    
    try:
        response = requests.post(api_url, json=invalid_us_data, headers=headers)
        if response.status_code == 400:
            print("✅ VALIDATION WORKING: HTTP 400 Bad Request")
            print(f"   Error details: {response.json()}")
        elif response.status_code == 201:
            print("❌ ERROR: Customer created when validation should have failed")
            print(f"   Created customer: {response.json().get('username')}")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()
    
    # Test 3: Valid Canadian postal code
    print("Test 3: Valid Canadian postal code (K1A 0A6 for CA)")
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
    
    try:
        response = requests.post(api_url, json=valid_ca_data, headers=headers)
        if response.status_code == 201:
            print("✅ VALIDATION WORKING: Valid postal code accepted")
            print(f"   Created customer: {response.json().get('username')}")
        else:
            print(f"❌ ERROR: Valid postal code rejected with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()
    
    # Test 4: Valid US ZIP code
    print("Test 4: Valid US ZIP code (90210 for US)")
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
    
    try:
        response = requests.post(api_url, json=valid_us_data, headers=headers)
        if response.status_code == 201:
            print("✅ VALIDATION WORKING: Valid ZIP code accepted")
            print(f"   Created customer: {response.json().get('username')}")
        else:
            print(f"❌ ERROR: Valid ZIP code rejected with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_postal_validation()