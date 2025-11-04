# Test driver registration endpoint
Write-Host "Testing driver registration endpoint..." -ForegroundColor Green

# Test driver registration data
$driverData = @{
    username = "newdriver.test"
    email = "newdriver@test.com"
    password = "testpass123"
    first_name = "New"
    last_name = "Driver"
    name = "New Driver"
    phone_number = "555-9999"
    license_number = "DL999999"
    vehicle_license_plate = "TEST999"
    vehicle_model = "Test Vehicle"
    vehicle_capacity = 1000
    vehicle_capacity_unit = "kg"
} | ConvertTo-Json

$headers = @{
    'Content-Type' = 'application/json'
}

try {
    Write-Host "Attempting driver registration..." -ForegroundColor Yellow
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/drivers/register/" -Method Post -Body $driverData -Headers $headers
    
    Write-Host "✓ Driver registration successful!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
    
} catch {
    Write-Host "✗ Driver registration failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody" -ForegroundColor Yellow
    }
}

Write-Host "`nNow testing login with the new driver credentials..." -ForegroundColor Green

# Test login with the new driver
$loginData = @{
    username = "newdriver.test"
    password = "testpass123"
} | ConvertTo-Json

try {
    Write-Host "Attempting driver login..." -ForegroundColor Yellow
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/token/" -Method Post -Body $loginData -Headers $headers
    
    Write-Host "✓ Driver login successful!" -ForegroundColor Green
    Write-Host "JWT Token obtained:" -ForegroundColor Cyan
    Write-Host "Access: $($loginResponse.access)" -ForegroundColor Gray
    
    # Test accessing authenticated endpoint
    $authHeaders = @{
        'Authorization' = "Bearer $($loginResponse.access)"
        'Content-Type' = 'application/json'
    }
    
    Write-Host "`nTesting access to drivers endpoint..." -ForegroundColor Green
    $driversResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/drivers/" -Method Get -Headers $authHeaders
    
    Write-Host "✓ Successfully accessed drivers endpoint!" -ForegroundColor Green
    Write-Host "Found $($driversResponse.count) total drivers" -ForegroundColor Cyan
    
} catch {
    Write-Host "✗ Driver login failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}