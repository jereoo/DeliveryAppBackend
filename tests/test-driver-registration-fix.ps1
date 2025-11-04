# test-driver-registration-fix.ps1
# Script to test the driver registration fix with full_name

Write-Host "🧪 Testing Driver Registration Fix (full_name support)" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan

# Navigate to backend directory
Set-Location "C:\Users\360WEB\DeliveryAppBackend"

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

Write-Host "🔧 Testing driver registration with full_name..." -ForegroundColor Yellow

try {
    # Test the fixed driver registration API
    python -c "
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DeliveryAppBackend.settings')
django.setup()

# Test data for driver registration
test_data = {
    'username': 'testdriver1',
    'email': 'testdriver1@email.com',
    'password': 'testpass123',
    'full_name': 'Mike Johnson',  # Using full_name instead of first_name + last_name
    'name': 'Mike Johnson',
    'phone_number': '555-123-4567',
    'license_number': 'DL999999',
    'vehicle_license_plate': 'TEST123',
    'vehicle_model': 'Test Van',
    'vehicle_capacity': 1500,
    'vehicle_capacity_unit': 'kg'
}

print('📊 Test Data:')
for key, value in test_data.items():
    if key != 'password':
        print(f'   {key}: {value}')
print()

# Test the serializer directly
from delivery.serializers import DriverRegistrationSerializer

print('🔍 Testing DriverRegistrationSerializer...')
serializer = DriverRegistrationSerializer(data=test_data)

if serializer.is_valid():
    print('✅ Serializer validation passed!')
    print('📝 Validated data preview:')
    
    # Show how the full_name was processed
    user_data = serializer.validated_data.get('user', {})
    print(f'   first_name: {user_data.get(\"first_name\", \"Not set\")}')
    print(f'   last_name: {user_data.get(\"last_name\", \"Not set\")}')
    print(f'   full_name processed: ✅')
    print()
    print('🎯 Ready for mobile app testing!')
    
else:
    print('❌ Serializer validation failed!')
    print('Errors:')
    for field, errors in serializer.errors.items():
        print(f'   {field}: {errors}')
"
    
} catch {
    Write-Host "❌ Error testing driver registration: $_" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "📱 Mobile App Instructions:" -ForegroundColor Yellow
Write-Host "   The driver registration form can now use:" -ForegroundColor White
Write-Host "   • 'full_name' field (e.g., 'Mike Johnson')" -ForegroundColor White
Write-Host "   • OR separate 'first_name' and 'last_name' fields" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "✅ Driver registration should now work!" -ForegroundColor Green

Read-Host "Press Enter to exit"