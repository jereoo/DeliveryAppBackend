# Test delivery request with better error handling
Write-Host "Testing delivery request..." -ForegroundColor Green

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
    
    $deliveryData = @{
        dropoff_location = "456 Destination Ave, Target City"
        same_pickup_as_customer = $true
        item_description = "Test Package"
        delivery_date = "2025-09-24"
        delivery_time = "14:00:00"
    } | ConvertTo-Json
    
    Write-Host "Delivery data:" -ForegroundColor Yellow
    Write-Host $deliveryData -ForegroundColor Gray
    
    $deliveryResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/deliveries/request_delivery/" -Method Post -Body $deliveryData -Headers $authHeaders
    
    Write-Host "✓ Delivery request successful!" -ForegroundColor Green
    $deliveryResponse | ConvertTo-Json -Depth 3
    
} catch {
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    # Try to get more error details
    if ($_.ErrorDetails) {
        Write-Host "Error Details:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Yellow
    }
}