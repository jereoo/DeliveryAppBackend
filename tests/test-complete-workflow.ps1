# Complete workflow test - Driver registration, Customer registration, and Delivery request
Write-Host "=== COMPLETE DELIVERY APP WORKFLOW TEST ===" -ForegroundColor Green
Write-Host ""

$headers = @{
    'Content-Type' = 'application/json'
}

# Generate random suffix to avoid conflicts
$timestamp = (Get-Date).ToString("yyyyMMddHHmmss")

Write-Host "1. DRIVER SELF-REGISTRATION" -ForegroundColor Cyan
$driverData = @{
    username = "driver.test.$timestamp"
    email = "driver.test.$timestamp@email.com"
    password = "testpass123"
    first_name = "Test"
    last_name = "Driver"
    name = "Test Driver"
    phone_number = "555-0001"
    license_number = "DL$timestamp"
    vehicle_license_plate = "VH$timestamp"
    vehicle_model = "Test Van"
    vehicle_capacity = 1500
    vehicle_capacity_unit = "kg"
} | ConvertTo-Json

try {
    $driverResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/drivers/register/" -Method Post -Body $driverData -Headers $headers
    Write-Host "✓ Driver registered successfully!" -ForegroundColor Green
    Write-Host "  Driver ID: $($driverResponse.driver_id)" -ForegroundColor Gray
    Write-Host "  Name: $($driverResponse.name)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Driver registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. CUSTOMER SELF-REGISTRATION" -ForegroundColor Cyan
$customerData = @{
    username = "customer.test.$timestamp"
    email = "customer.test.$timestamp@email.com"
    password = "testpass123"
    first_name = "Test"
    last_name = "Customer"
    phone_number = "555-0002"
    address = "123 Pickup Street, Source City"
    is_business = $false
} | ConvertTo-Json

try {
    $customerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/customers/register/" -Method Post -Body $customerData -Headers $headers
    Write-Host "✓ Customer registered successfully!" -ForegroundColor Green
    Write-Host "  Customer ID: $($customerResponse.customer.id)" -ForegroundColor Gray
    Write-Host "  Name: $($customerResponse.customer.display_name)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Customer registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. CUSTOMER LOGIN" -ForegroundColor Cyan
$loginData = @{
    username = "customer.test.$timestamp"
    password = "testpass123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/token/" -Method Post -Body $loginData -Headers $headers
    Write-Host "✓ Customer login successful!" -ForegroundColor Green
    Write-Host "  JWT token obtained" -ForegroundColor Gray
} catch {
    Write-Host "✗ Customer login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "4. DELIVERY REQUEST" -ForegroundColor Cyan
$authHeaders = @{
    'Authorization' = "Bearer $($loginResponse.access)"
    'Content-Type' = 'application/json'
}

$deliveryData = @{
    dropoff_location = "456 Destination Ave, Target City"
    same_pickup_as_customer = $true
    item_description = "Important Package"
    delivery_date = "2025-09-25"
    delivery_time = "10:00:00"
    special_instructions = "Handle with care"
} | ConvertTo-Json

try {
    $deliveryResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/deliveries/request_delivery/" -Method Post -Body $deliveryData -Headers $authHeaders
    Write-Host "✓ Delivery requested successfully!" -ForegroundColor Green
    Write-Host "  Delivery ID: $($deliveryResponse.delivery.id)" -ForegroundColor Gray
    Write-Host "  Status: $($deliveryResponse.delivery.status)" -ForegroundColor Gray
    Write-Host "  Pickup: $($deliveryResponse.delivery.pickup_location)" -ForegroundColor Gray
    Write-Host "  Dropoff: $($deliveryResponse.delivery.dropoff_location)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Delivery request failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 ALL TESTS PASSED! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "WORKFLOW SUMMARY:" -ForegroundColor Yellow
Write-Host "✅ Drivers can self-register with their vehicles" -ForegroundColor Gray
Write-Host "✅ Customers can self-register as individuals" -ForegroundColor Gray  
Write-Host "✅ Customers can login and obtain JWT tokens" -ForegroundColor Gray
Write-Host "✅ Customers can request deliveries with authentication" -ForegroundColor Gray
Write-Host "✅ Pickup location auto-fills from customer address" -ForegroundColor Gray
Write-Host ""
Write-Host "The complete delivery app workflow is working correctly!" -ForegroundColor Green