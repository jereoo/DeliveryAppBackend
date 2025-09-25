# Test customer registration and delivery request workflow
Write-Host "Testing complete customer workflow..." -ForegroundColor Green

# Test customer registration data
$customerData = @{
    username = "testcustomer.new"
    email = "testcustomer@test.com"
    password = "testpass123"
    first_name = "Test"
    last_name = "Customer"
    phone_number = "555-8888"
    address = "123 Test Street, Test City"
    is_business = $false
} | ConvertTo-Json

$headers = @{
    'Content-Type' = 'application/json'
}

try {
    Write-Host "Step 1: Customer registration..." -ForegroundColor Yellow
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/customers/register/" -Method Post -Body $customerData -Headers $headers
    
    Write-Host "✓ Customer registration successful!" -ForegroundColor Green
    Write-Host "Customer ID: $($response.id)" -ForegroundColor Cyan
    
    # Test login with the new customer
    $loginData = @{
        username = "testcustomer.new"
        password = "testpass123"
    } | ConvertTo-Json
    
    Write-Host "Step 2: Customer login..." -ForegroundColor Yellow
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/token/" -Method Post -Body $loginData -Headers $headers
    
    Write-Host "✓ Customer login successful!" -ForegroundColor Green
    
    # Test delivery request
    $authHeaders = @{
        'Authorization' = "Bearer $($loginResponse.access)"
        'Content-Type' = 'application/json'
    }
    
    $deliveryData = @{
        dropoff_location = "456 Destination Ave, Target City"
        same_pickup_as_customer = $true
        item_description = "Test Package"
        delivery_date = "2025-09-24"
        delivery_time = "14:00:00"
    } | ConvertTo-Json
    
    Write-Host "Step 3: Delivery request..." -ForegroundColor Yellow
    
    $deliveryResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/deliveries/request_delivery/" -Method Post -Body $deliveryData -Headers $authHeaders
    
    Write-Host "✓ Delivery request successful!" -ForegroundColor Green
    Write-Host "Delivery ID: $($deliveryResponse.id)" -ForegroundColor Cyan
    Write-Host "Status: $($deliveryResponse.status)" -ForegroundColor Cyan
    Write-Host "Pickup: $($deliveryResponse.pickup_location)" -ForegroundColor Cyan
    Write-Host "Dropoff: $($deliveryResponse.dropoff_location)" -ForegroundColor Cyan
    
    Write-Host "`n🎉 Complete workflow test successful!" -ForegroundColor Green
    Write-Host "✓ Customer can register" -ForegroundColor Gray
    Write-Host "✓ Customer can login and get JWT token" -ForegroundColor Gray
    Write-Host "✓ Customer can request delivery with authentication" -ForegroundColor Gray
    
} catch {
    Write-Host "✗ Workflow test failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody" -ForegroundColor Yellow
    }
}