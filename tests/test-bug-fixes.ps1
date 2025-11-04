# Test Bug Fixes Script
# Tests the postal code validation and customer account activation fixes

Write-Host "🧪 TESTING BUG FIXES" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

$serverURL = "http://192.168.1.77:8081"

# Test 1: Canadian Postal Code Validation
Write-Host "`n📍 Test 1: Canadian Postal Code Registration" -ForegroundColor Yellow

$canadianCustomer = @{
  user                = @{
    username   = "testcanada"
    email      = "test@canada.ca"
    password   = "testpass123"
    first_name = "John"
    last_name  = "Canada"
  }
  phone_number        = "555-0123"
  address_street      = "123 Maple St"
  address_city        = "Toronto"
  address_state       = "ON"
  address_postal_code = "A1A 1A1"
  address_country     = "CA"
  is_business         = $false
} | ConvertTo-Json -Depth 3

try {
  $response = Invoke-WebRequest -Uri "$serverURL/api/customers/register/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $canadianCustomer -TimeoutSec 10
  Write-Host "✅ Canadian postal code registration successful!" -ForegroundColor Green
  $customerData = $response.Content | ConvertFrom-Json
  Write-Host "Customer ID: $($customerData.id)" -ForegroundColor Gray
}
catch {
  Write-Host "❌ Canadian postal code registration failed!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Customer Login Test  
Write-Host "`n🔐 Test 2: Customer Login Test" -ForegroundColor Yellow

$loginData = @{
  username = "testcanada"
  password = "testpass123"
} | ConvertTo-Json

try {
  $loginResponse = Invoke-WebRequest -Uri "$serverURL/api/token/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $loginData -TimeoutSec 10
  Write-Host "✅ Customer login successful!" -ForegroundColor Green
  $tokenData = $loginResponse.Content | ConvertFrom-Json
  Write-Host "Access token received: $($tokenData.access.Substring(0,20))..." -ForegroundColor Gray
}
catch {
  Write-Host "❌ Customer login failed!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: US ZIP Code Test
Write-Host "`n📍 Test 3: US ZIP Code Registration" -ForegroundColor Yellow

$usCustomer = @{
  user                = @{
    username   = "testusa"
    email      = "test@usa.com"
    password   = "testpass123"
    first_name = "Jane"
    last_name  = "America"
  }
  phone_number        = "555-0456"
  address_street      = "456 Main St"
  address_city        = "New York"
  address_state       = "NY"
  address_postal_code = "12345"
  address_country     = "US"
  is_business         = $false
} | ConvertTo-Json -Depth 3

try {
  $response = Invoke-WebRequest -Uri "$serverURL/api/customers/register/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $usCustomer -TimeoutSec 10
  Write-Host "✅ US ZIP code registration successful!" -ForegroundColor Green
}
catch {
  Write-Host "❌ US ZIP code registration failed!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 BUG FIX TESTING COMPLETE!" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Cyan