# Backend API Development Testing (bypasses public WiFi restrictions)
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from delivery.models import Customer, Driver, Vehicle, Delivery
import json

print('=== BACKEND API DEVELOPMENT TESTING ===')

# Create test client
client = APIClient()
user = User.objects.get(username='admin')
token = str(RefreshToken.for_user(user).access_token)
client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

# Test 1: Customer Registration
print('\n1. Testing Customer Registration...')
customer_data = {
    'username': 'testcust456',
    'email': 'test456@customer.com', 
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'Customer',
    'phone_number': '555-0001',
    'address': '123 Test St',
    'is_business': False
}

response = client.post('/api/customers/register/', customer_data, format='json')
print(f'   Status: {response.status_code}')
if response.status_code == 201:
    print(f'   ✅ Customer created successfully')
else:
    print(f'   Response: {response.content.decode()}')

# Test 2: Driver Registration  
print('\n2. Testing Driver Registration...')
driver_data = {
    'username': 'testdriver456',
    'email': 'driver456@test.com',
    'password': 'testpass123', 
    'first_name': 'Test',
    'last_name': 'Driver',
    'name': 'Test Driver 456',
    'phone_number': '555-0002',
    'license_number': 'DL456789',
    'vehicle_license_plate': 'ABC456',
    'vehicle_model': 'Test Van 456',
    'vehicle_capacity': 1500,
    'vehicle_capacity_unit': 'kg'
}

response = client.post('/api/drivers/register/', driver_data, format='json')
print(f'   Status: {response.status_code}')
if response.status_code == 201:
    print(f'   ✅ Driver created successfully')
else:
    print(f'   Response: {response.content.decode()}')

# Test 3: List all data
print('\n3. Testing Data Retrieval...')
endpoints = [
    ('/api/customers/', 'Customers'),
    ('/api/drivers/', 'Drivers'),
    ('/api/vehicles/', 'Vehicles'),
    ('/api/deliveries/', 'Deliveries')
]

for endpoint, name in endpoints:
    response = client.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', len(data) if isinstance(data, list) else 'N/A')
        print(f'   ✅ {name}: {count} records')
    else:
        print(f'   ❌ {name}: Status {response.status_code}')

# Test 4: Model counts from database
print('\n4. Direct Database Counts...')
print(f'   Users: {User.objects.count()}')
print(f'   Customers: {Customer.objects.count()}')
print(f'   Drivers: {Driver.objects.count()}')
print(f'   Vehicles: {Vehicle.objects.count()}')
print(f'   Deliveries: {Delivery.objects.count()}')

print('\n✅ Backend development testing complete!')
print('This bypasses all network restrictions and tests your API directly.')