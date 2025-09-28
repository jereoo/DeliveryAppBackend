#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the path
sys.path.append('.')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DeliveryAppBackend.settings')
django.setup()

from rest_framework.test import APIClient
from delivery.serializers import CustomerRegistrationSerializer
from django.contrib.auth.models import User

print('=== CUSTOMER REGISTRATION DEBUG ===')

# Test data
customer_data = {
    'username': 'testcust999',
    'email': 'test999@customer.com',
    'password': 'testpass123',
    'first_name': 'Test',
    'last_name': 'Customer',
    'phone_number': '555-0001',
    'address': '123 Test St, Test City',
    'is_business': False
}

print('1. Testing serializer validation...')
serializer = CustomerRegistrationSerializer(data=customer_data)

if serializer.is_valid():
    print('✅ Serializer validation passed')
    try:
        customer = serializer.save()
        print(f'✅ Customer created: ID={customer.id}, Username={customer.user.username}')
    except Exception as e:
        print(f'❌ Customer creation failed: {e}')
        import traceback
        traceback.print_exc()
else:
    print(f'❌ Serializer validation failed: {serializer.errors}')

print('\n2. Testing via API client...')
client = APIClient()
response = client.post('/api/customers/register/', customer_data, format='json')
print(f'API Response: Status {response.status_code}')
if response.status_code != 201:
    print(f'Error: {response.content.decode()}')
else:
    print('✅ API registration successful')
    print(f'Response: {response.json()}')

print('\n3. Database stats:')
from delivery.models import Customer
print(f'Total customers: {Customer.objects.count()}')
print(f'Total users: {User.objects.count()}')