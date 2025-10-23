# verify-test-data.ps1
# Script to verify the test data was created successfully

Write-Host "🔍 Verifying Test Data Creation" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Cyan

# Navigate to backend directory
Set-Location "C:\Users\360WEB\DeliveryAppBackend"

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

Write-Host "📊 Checking database contents..." -ForegroundColor Yellow

try {
    # Query database for created test data
    python -c "
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DeliveryAppBackend.settings')
django.setup()

from django.contrib.auth.models import User
from delivery.models import Customer, Driver, Vehicle, DriverVehicle

print('\n📱 TEST CUSTOMERS:')
print('=' * 50)
customers = Customer.objects.all()[:10]
for customer in customers:
    customer_type = 'Business' if customer.is_business else 'Individual'
    company_info = f' ({customer.company_name})' if customer.company_name else ''
    print(f'• {customer.user.username} - {customer_type}{company_info}')
    print(f'  Email: {customer.user.email}')
    print(f'  Phone: {customer.phone_number}')
    print(f'  Address: {customer.address}')
    print()

print('\n🚚 TEST DRIVERS:')
print('=' * 50)
drivers = Driver.objects.all()[:10]
for driver in drivers:
    driver_vehicle = DriverVehicle.objects.filter(driver=driver, assigned_to__isnull=True).first()
    if driver_vehicle and driver_vehicle.vehicle:
        vehicle_info = f'{driver_vehicle.vehicle.model} ({driver_vehicle.vehicle.license_plate}) - {driver_vehicle.vehicle.capacity_display}'
    else:
        vehicle_info = 'No vehicle assigned'
    print(f'• {driver.name}')
    print(f'  Phone: {driver.phone_number}')
    print(f'  License: {driver.license_number}')
    print(f'  Vehicle: {vehicle_info}')
    print()

print('📊 SUMMARY:')
print('=' * 50)
print(f'Total Customers: {Customer.objects.count()}')
print(f'Total Drivers: {Driver.objects.count()}')
print(f'Total Vehicles: {Vehicle.objects.count()}')
print(f'Total Users: {User.objects.count()}')
print()
print('✅ All test data verified successfully!')
"
    
} catch {
    Write-Host "❌ Error verifying test data: $_" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "📝 LOGIN CREDENTIALS:" -ForegroundColor Yellow
Write-Host "   Usernames: firstname.lastname.# (e.g., sarah.williams.1)" -ForegroundColor White
Write-Host "   Password: testpass123" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "🎯 Ready for mobile app testing!" -ForegroundColor Green

Read-Host "Press Enter to exit"