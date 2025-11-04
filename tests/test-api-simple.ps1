# 🧪 Simple API Testing Script

Write-Host "🧪 TESTING DELIVERYAPP API" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:8000"
$testResults = @()

# Test 1: Backend Connectivity
Write-Host "`n🔗 Testing Backend Connectivity..." -ForegroundColor Yellow
try {
  $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/" -Method GET -TimeoutSec 5
  Write-Host "✅ Backend accessible" -ForegroundColor Green
  $testResults += "Backend Connection: PASS"
}
catch {
  Write-Host "❌ Backend not accessible: $($_.Exception.Message)" -ForegroundColor Red
  $testResults += "Backend Connection: FAIL"
}

# Test 2: Customer Registration
Write-Host "`n👤 Testing Customer Registration..." -ForegroundColor Yellow
$customerData = @{
  username      = "testuser$(Get-Random -Minimum 1000 -Maximum 9999)"
  password      = "testpass123"
  email         = "test@example.com"
  first_name    = "Test"
  last_name     = "User"
  address       = "123 Test St"
  phone         = "555-0123"
  customer_type = "individual"
}

try {
  $regResponse = Invoke-RestMethod -Uri "$baseUrl/api/customers/register/" -Method POST -Body ($customerData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 10
  Write-Host "✅ Customer registration successful" -ForegroundColor Green
  $testResults += "Customer Registration: PASS"
  $testUsername = $customerData.username
  $testPassword = $customerData.password
}
catch {
  Write-Host "❌ Customer registration failed: $($_.Exception.Message)" -ForegroundColor Red
  $testResults += "Customer Registration: FAIL"
}

# Test 3: Authentication
if ($testUsername) {
  Write-Host "`n🔐 Testing Authentication..." -ForegroundColor Yellow
  $loginData = @{
    username = $testUsername
    password = $testPassword
  }
    
  try {
    $authResponse = Invoke-RestMethod -Uri "$baseUrl/api/token/" -Method POST -Body ($loginData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Authentication successful" -ForegroundColor Green
    $testResults += "Authentication: PASS"
    $token = $authResponse.access
  }
  catch {
    Write-Host "❌ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    $testResults += "Authentication: FAIL"
  }
}

# Test 4: Profile Access
if ($token) {
  Write-Host "`n📖 Testing Profile Access..." -ForegroundColor Yellow
  try {
    $headers = @{ "Authorization" = "Bearer $token" }
    $profileResponse = Invoke-RestMethod -Uri "$baseUrl/api/customers/me/" -Method GET -Headers $headers -TimeoutSec 10
    Write-Host "✅ Profile access successful" -ForegroundColor Green
    $testResults += "Profile Access: PASS"
  }
  catch {
    Write-Host "❌ Profile access failed: $($_.Exception.Message)" -ForegroundColor Red
    $testResults += "Profile Access: FAIL"
  }
}

# Summary
Write-Host "`n📊 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan
foreach ($result in $testResults) {
  if ($result -like "*PASS*") {
    Write-Host $result -ForegroundColor Green
  }
  else {
    Write-Host $result -ForegroundColor Red
  }
}

$passCount = ($testResults | Where-Object { $_ -like "*PASS*" }).Count
$totalCount = $testResults.Count
$successRate = [math]::Round(($passCount / $totalCount) * 100, 1)

Write-Host "`n🎯 Success Rate: $successRate% ($passCount/$totalCount)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Red" })

if ($successRate -ge 80) {
  Write-Host "`n🎉 API TESTING SUCCESSFUL!" -ForegroundColor Green
  Write-Host "✅ Backend is ready for mobile app testing" -ForegroundColor Green
}
else {
  Write-Host "`n⚠️ Some tests failed. Check backend configuration." -ForegroundColor Yellow
}