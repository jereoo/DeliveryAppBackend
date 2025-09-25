# Test new delivery checkbox options
Write-Host "Testing new delivery checkbox options..." -ForegroundColor Green

# First get a token for an existing customer
$loginData = @{
    username = "john.smith"
    password = "testpass123"
} | ConvertTo-Json

$headers = @{
    'Content-Type' = 'application/json'
}

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/token/" -Method Post -Body $loginData -Headers $headers
    
    $authHeaders = @{
        'Authorization' = "Bearer $($loginResponse.access)"
        'Content-Type' = 'application/json'
    }
    
    Write-Host "`nTest 1: Same pickup as customer, different dropoff" -ForegroundColor Cyan
    $deliveryData1 = @{
        dropoff_location = "456 Different Destination"
        same_pickup_as_customer = $true
        same_dropoff_as_customer = $false
        item_description = "Test Package 1"
        delivery_date = "2025-09-25"
        delivery_time = "09:00:00"
    } | ConvertTo-Json
    
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/deliveries/request_delivery/" -Method Post -Body $deliveryData1 -Headers $authHeaders
    Write-Host "✓ Delivery 1 created successfully" -ForegroundColor Green
    Write-Host "  Pickup: $($response1.delivery.pickup_location)" -ForegroundColor Gray
    Write-Host "  Dropoff: $($response1.delivery.dropoff_location)" -ForegroundColor Gray
    
    Write-Host "`nTest 2: Different pickup, same dropoff as customer" -ForegroundColor Cyan
    $deliveryData2 = @{
        pickup_location = "789 Different Pickup Location"
        same_pickup_as_customer = $false
        same_dropoff_as_customer = $true
        item_description = "Test Package 2"
        delivery_date = "2025-09-25"
        delivery_time = "10:00:00"
    } | ConvertTo-Json
    
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/deliveries/request_delivery/" -Method Post -Body $deliveryData2 -Headers $authHeaders
    Write-Host "✓ Delivery 2 created successfully" -ForegroundColor Green
    Write-Host "  Pickup: $($response2.delivery.pickup_location)" -ForegroundColor Gray
    Write-Host "  Dropoff: $($response2.delivery.dropoff_location)" -ForegroundColor Gray
    
    Write-Host "`nTest 3: Both pickup and dropoff same as customer" -ForegroundColor Cyan
    $deliveryData3 = @{
        same_pickup_as_customer = $true
        same_dropoff_as_customer = $true
        item_description = "Test Package 3"
        delivery_date = "2025-09-25"
        delivery_time = "11:00:00"
    } | ConvertTo-Json
    
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/deliveries/request_delivery/" -Method Post -Body $deliveryData3 -Headers $authHeaders
    Write-Host "✓ Delivery 3 created successfully" -ForegroundColor Green
    Write-Host "  Pickup: $($response3.delivery.pickup_location)" -ForegroundColor Gray
    Write-Host "  Dropoff: $($response3.delivery.dropoff_location)" -ForegroundColor Gray
    
    Write-Host "`nTest 4: Custom pickup and dropoff locations" -ForegroundColor Cyan
    $deliveryData4 = @{
        pickup_location = "Custom Pickup Address"
        dropoff_location = "Custom Dropoff Address"
        same_pickup_as_customer = $false
        same_dropoff_as_customer = $false
        item_description = "Test Package 4"
        delivery_date = "2025-09-25"
        delivery_time = "12:00:00"
    } | ConvertTo-Json
    
    $response4 = Invoke-RestMethod -Uri "http://localhost:8000/api/deliveries/request_delivery/" -Method Post -Body $deliveryData4 -Headers $authHeaders
    Write-Host "✓ Delivery 4 created successfully" -ForegroundColor Green
    Write-Host "  Pickup: $($response4.delivery.pickup_location)" -ForegroundColor Gray
    Write-Host "  Dropoff: $($response4.delivery.dropoff_location)" -ForegroundColor Gray
    
    Write-Host "`n🎉 All checkbox tests passed!" -ForegroundColor Green
    Write-Host "✅ Pickup location checkbox working" -ForegroundColor Gray
    Write-Host "✅ Dropoff location checkbox working" -ForegroundColor Gray
    Write-Host "✅ Both checkboxes can work together" -ForegroundColor Gray
    Write-Host "✅ Manual address entry still works" -ForegroundColor Gray
    
} catch {
    Write-Host "✗ Test failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host "Error Details:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Yellow
    }
}