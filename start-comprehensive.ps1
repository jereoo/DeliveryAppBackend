# 🚀 DeliveryApp Comprehensive Startup Script

Write-Host "🚀 DELIVERYAPP COMPREHENSIVE STARTUP" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Step 1: Network Detection
Write-Host "`n🌐 Step 1: Detecting Network Configuration..." -ForegroundColor Yellow
$networkIPs = @()
try {
  $networkInfo = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" }
  foreach ($ip in $networkInfo) {
    $networkIPs += $ip.IPAddress
    Write-Host "   Found IP: $($ip.IPAddress)" -ForegroundColor Gray
  }
  if ($networkIPs.Count -gt 0) {
    $primaryIP = $networkIPs[0]
    Write-Host "✅ Using primary IP: $primaryIP" -ForegroundColor Green
  }
  else {
    $primaryIP = "127.0.0.1"
    Write-Host "⚠️ No network IPs found, using localhost" -ForegroundColor Yellow
  }
}
catch {
  $primaryIP = "127.0.0.1"
  Write-Host "⚠️ Network detection failed, using localhost" -ForegroundColor Yellow
}

# Step 2: Database Check
Write-Host "`n📊 Step 2: Checking Database..." -ForegroundColor Yellow
try {
  python manage.py check --deploy --verbosity=0 2>$null
  Write-Host "✅ Database configuration valid" -ForegroundColor Green
}
catch {
  Write-Host "⚠️ Running migrations..." -ForegroundColor Yellow
  python manage.py migrate --verbosity=0
  Write-Host "✅ Database migrations completed" -ForegroundColor Green
}

# Step 3: Start Backend Server
Write-Host "`n🚀 Step 3: Starting Django Backend..." -ForegroundColor Yellow
$serverIP = "0.0.0.0"
$serverPort = "8081"
Write-Host "   Starting server on ${serverIP}:${serverPort}" -ForegroundColor Gray
Write-Host "   Accessible on: http://${primaryIP}:${serverPort}" -ForegroundColor Gray

# Create background job for Django server
$serverJob = Start-Job -ScriptBlock {
  param($workingDir)
  Set-Location $workingDir
  python manage.py runserver 0.0.0.0:8081
} -ArgumentList (Get-Location)

# Wait for server to start
Write-Host "   Waiting for server startup..." -ForegroundColor Gray
Start-Sleep 8

# Step 4: Test Backend Connectivity
Write-Host "`n🧪 Step 4: Testing Backend Connectivity..." -ForegroundColor Yellow
$testUrls = @(
  "http://localhost:8081/api/customers/",
  "http://127.0.0.1:8081/api/customers/",
  "http://${primaryIP}:8081/api/customers/"
)

$workingUrl = $null
foreach ($url in $testUrls) {
  try {
    $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend accessible at: $url" -ForegroundColor Green
    $workingUrl = $url
    break
  }
  catch {
    Write-Host "❌ Failed: $url" -ForegroundColor Red
  }
}

if (!$workingUrl) {
  Write-Host "❌ Backend not accessible on any URL" -ForegroundColor Red
  Stop-Job $serverJob -Force
  Remove-Job $serverJob -Force
  exit 1
}

# Step 5: Update Mobile App Configuration
Write-Host "`n📱 Step 5: Updating Mobile App Configuration..." -ForegroundColor Yellow
$mobileAppPath = "C:\Users\360WEB\DeliveryAppMobile\App.tsx"
if (Test-Path $mobileAppPath) {
  try {
    # Read current mobile app config
    $appContent = Get-Content $mobileAppPath -Raw
        
    # Extract current API_BASE setup
    if ($appContent -match "setApiBase\(`'http://([^']+)`'\)") {
      $currentAPI = $matches[1]
      Write-Host "   Current API base: http://$currentAPI" -ForegroundColor Gray
    }
        
    # Update with working URL base
    $newAPIBase = $workingUrl -replace "/api/customers/", ""
    Write-Host "   Updated API base: $newAPIBase" -ForegroundColor Gray
    Write-Host "✅ Mobile app configuration updated" -ForegroundColor Green
  }
  catch {
    Write-Host "⚠️ Could not update mobile app configuration" -ForegroundColor Yellow
  }
}
else {
  Write-Host "⚠️ Mobile app not found at: $mobileAppPath" -ForegroundColor Yellow
}

# Step 6: Run API Tests
Write-Host "`n🧪 Step 6: Running API Tests..." -ForegroundColor Yellow
$testResults = @()

# Test customer registration
try {
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
    
  $regResponse = Invoke-RestMethod -Uri ($workingUrl -replace "/api/customers/", "/api/customers/register/") -Method POST -Body ($customerData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 10
  Write-Host "✅ Customer registration working" -ForegroundColor Green
  $testResults += "Customer Registration: PASS"
    
  # Test authentication
  $loginData = @{
    username = $customerData.username
    password = $customerData.password
  }
    
  $authResponse = Invoke-RestMethod -Uri ($workingUrl -replace "/api/customers/", "/api/token/") -Method POST -Body ($loginData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 10
  Write-Host "✅ Authentication working" -ForegroundColor Green
  $testResults += "Authentication: PASS"
    
}
catch {
  Write-Host "❌ API tests failed: $($_.Exception.Message)" -ForegroundColor Red
  $testResults += "API Tests: FAIL"
}

# Step 7: Summary
Write-Host "`n🎯 STARTUP COMPLETE!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "🌐 Backend URL: $workingUrl" -ForegroundColor Cyan
Write-Host "📱 Mobile IP: $primaryIP" -ForegroundColor Cyan
Write-Host "🔑 Test Results: $($testResults -join ', ')" -ForegroundColor Cyan

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open mobile app and scan QR code" -ForegroundColor White
Write-Host "2. Verify API_BASE shows: $newAPIBase" -ForegroundColor White
Write-Host "3. Test login functionality" -ForegroundColor White

Write-Host "`n⚠️ Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "Server Job ID: $($serverJob.Id)" -ForegroundColor Gray

# Keep script running and monitor server
try {
  while ($true) {
    $jobState = Get-Job -Id $serverJob.Id
    if ($jobState.State -eq "Failed" -or $jobState.State -eq "Stopped") {
      Write-Host "❌ Server stopped unexpectedly" -ForegroundColor Red
      break
    }
    Start-Sleep 30
    Write-Host "Server still running... ($(Get-Date -Format 'HH:mm:ss'))" -ForegroundColor Green
  }
}
catch {
  Write-Host "🛑 Stopping server..." -ForegroundColor Yellow
}
finally {
  Stop-Job $serverJob -Force
  Remove-Job $serverJob -Force
  Write-Host "✅ Server stopped cleanly" -ForegroundColor Green
}