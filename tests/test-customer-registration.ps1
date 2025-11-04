# Simple customer registration test
$customerData = @{
    username = "testcustomer.new2"
    email = "testcustomer2@test.com"
    password = "testpass123"
    first_name = "Test2"
    last_name = "Customer2"
    phone_number = "555-7777"
    address = "123 Test Street, Test City"
    is_business = $false
} | ConvertTo-Json

$headers = @{
    'Content-Type' = 'application/json'
}

try {
    Write-Host "Customer registration data:" -ForegroundColor Yellow
    Write-Host $customerData -ForegroundColor Gray
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/customers/register/" -Method Post -Body $customerData -Headers $headers
    Write-Host "✓ Success!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
    
} catch {
    Write-Host "Registration failed:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host "Error Details:" -ForegroundColor Yellow  
        Write-Host $_.ErrorDetails.Message -ForegroundColor Yellow
    }
}