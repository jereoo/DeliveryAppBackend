# test-data-creation.ps1
# Script to create test data for the DeliveryApp mobile application

Write-Host "🧪 Creating Test Data for DeliveryApp Mobile" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# Navigate to backend directory
Set-Location "C:\Users\360WEB\DeliveryAppBackend"

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "📊 Creating test customers and drivers..." -ForegroundColor Yellow

try {
    # Create test data (10 customers, 10 drivers with vehicles)
    python manage.py create_test_data --customers 10 --drivers 10
    
    Write-Host "" -ForegroundColor White
    Write-Host "✅ Test data created successfully!" -ForegroundColor Green
    Write-Host "" -ForegroundColor White
    Write-Host "📱 TEST ACCOUNTS CREATED:" -ForegroundColor Cyan
    Write-Host "   Username format: firstname.lastname.1" -ForegroundColor White
    Write-Host "   Password: testpass123" -ForegroundColor White
    Write-Host "   Examples: john.smith.1, jane.johnson.2, etc." -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "🚚 DRIVER DATA:" -ForegroundColor Cyan
    Write-Host "   10 drivers with assigned vehicles" -ForegroundColor White
    Write-Host "   Various vehicle types and capacities" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "🎯 READY FOR MOBILE TESTING!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error creating test data: $_" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "📝 To clear and recreate data, run:" -ForegroundColor Yellow
Write-Host "   python manage.py create_test_data --clear --customers 10 --drivers 10" -ForegroundColor White

Read-Host "Press Enter to exit"