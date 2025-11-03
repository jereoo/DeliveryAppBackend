# Test Country Code Fix
# Verifies that the country code selector fix resolves the validation error

Write-Host "🌍 TESTING COUNTRY CODE FIX" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

$serverURL = "http://192.168.1.77:8081"

# Test Canadian Customer with Correct Country Code
Write-Host "`n🇨🇦 Test: Canadian Customer Registration" -ForegroundColor Yellow

$canadianCustomer = @{
  user                = @{
    username   = "testcanada2"
    email      = "test2@canada.ca"
    password   = "testpass123"
    first_name = "Sarah"
    last_name  = "Maple"
  }
  phone_number        = "555-0789"
  address_street      = "456 Hockey St"
  address_city        = "Vancouver"
  address_state       = "BC"
  address_postal_code = "V6B 1A1"
  address_country     = "CA"
  is_business         = $false
} | ConvertTo-Json -Depth 3

try {
  $response = Invoke-WebRequest -Uri "$serverURL/api/customers/register/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $canadianCustomer -TimeoutSec 10
  Write-Host "✅ Canadian customer registration SUCCESS!" -ForegroundColor Green
  $customerData = $response.Content | ConvertFrom-Json
  Write-Host "Customer ID: $($customerData.id), Country: $($customerData.address_country)" -ForegroundColor Gray
}
catch {
  Write-Host "❌ Canadian customer registration FAILED!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
  if ($_.Exception.Response) {
    $errorContent = $_.Exception.Response.Content.ReadAsStringAsync().Result
    Write-Host "Response: $errorContent" -ForegroundColor Red
  }
}

# Test US Customer with Correct Country Code
Write-Host "`n🇺🇸 Test: US Customer Registration" -ForegroundColor Yellow

$usCustomer = @{
  user                = @{
    username   = "testusa2"
    email      = "test2@usa.com"
    password   = "testpass123"
    first_name = "John"
    last_name  = "Freedom"
  }
  phone_number        = "555-0123"
  address_street      = "789 Liberty Ave"
  address_city        = "New York"
  address_state       = "NY"
  address_postal_code = "10001"
  address_country     = "US"
  is_business         = $false
} | ConvertTo-Json -Depth 3

try {
  $response = Invoke-WebRequest -Uri "$serverURL/api/customers/register/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $usCustomer -TimeoutSec 10
  Write-Host "✅ US customer registration SUCCESS!" -ForegroundColor Green
  $customerData = $response.Content | ConvertFrom-Json
  Write-Host "Customer ID: $($customerData.id), Country: $($customerData.address_country)" -ForegroundColor Gray
}
catch {
  Write-Host "❌ US customer registration FAILED!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Login for Canadian Customer
Write-Host "`n🔐 Test: Canadian Customer Login" -ForegroundColor Yellow

$loginData = @{
  username = "testcanada2"
  password = "testpass123"
} | ConvertTo-Json

try {
  $loginResponse = Invoke-WebRequest -Uri "$serverURL/api/token/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $loginData -TimeoutSec 10
  Write-Host "✅ Canadian customer login SUCCESS!" -ForegroundColor Green
  $tokenData = $loginResponse.Content | ConvertFrom-Json
  Write-Host "Token received and login working!" -ForegroundColor Gray
}
catch {
  Write-Host "❌ Canadian customer login FAILED!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 COUNTRY CODE FIX TESTING COMPLETE!" -ForegroundColor Green
Write-Host "Country selector buttons should now work in mobile app!" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Cyan