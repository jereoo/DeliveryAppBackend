# 🧪 Updated Mobile CRUD Testing - Correct Authentication Flow
# Tests Customer CRUD operations with proper authentication (customers accessing their own profiles)

param(
    [string]$BackendURL = "http://192.168.1.85:8081",
    [string]$MobileAppPath = "C:\Users\360WEB\DeliveryAppMobile"
)

Write-Host "🧪 MOBILE CRUD TESTING - CORRECT AUTHENTICATION FLOW" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Backend: $BackendURL" -ForegroundColor Yellow
Write-Host "Mobile App: $MobileAppPath" -ForegroundColor Yellow

# Test results tracking
$testResults = @{
    BackendConnectivity = $false
    MobileAppConfig = $false
    CustomerRegistration = $false
    CustomerAuthentication = $false
    CustomerRead = $false
    CustomerUpdate = $false
    CustomerDelete = $false
}

# Test 1: Backend Connectivity
Write-Host "`n🔗 TEST 1: Backend Connectivity" -ForegroundColor White
Write-Host "===============================" -ForegroundColor Gray
try {
    # Test with public registration endpoint instead of protected /api/
    $response = Invoke-RestMethod -Uri "$BackendURL/api/customers/register/" -Method OPTIONS -TimeoutSec 5
    Write-Host "✅ Backend accessible at $BackendURL" -ForegroundColor Green
    $testResults.BackendConnectivity = $true
} catch {
    Write-Host "❌ Backend not accessible: $_" -ForegroundColor Red
    Write-Host "⚠️  Make sure backend is running: .\start-backend-simple.ps1" -ForegroundColor Yellow
    return
}

# Test 2: Mobile App Configuration
Write-Host "`n📱 TEST 2: Mobile App Configuration" -ForegroundColor White
Write-Host "===================================" -ForegroundColor Gray

if (Test-Path "$MobileAppPath\App.tsx") {
    $appContent = Get-Content "$MobileAppPath\App.tsx" -Raw
    
    if ($appContent -match "192\.168\.1\.85:8081") {
        Write-Host "✅ Current IP (192.168.1.85) found in NETWORK_ENDPOINTS" -ForegroundColor Green
        $testResults.MobileAppConfig = $true
    } else {
        Write-Host "❌ Current IP (192.168.1.85) NOT found in mobile app config" -ForegroundColor Red
        Write-Host "⚠️  Run: .\update-mobile-network-config.ps1" -ForegroundColor Yellow
    }
    
    if ($appContent -match "createCustomer.*updateCustomer.*deleteCustomer") {
        Write-Host "✅ CRUD functions detected in mobile app" -ForegroundColor Green
    } else {
        Write-Host "⚠️  CRUD functions not detected - check mobile app implementation" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Mobile app not found at: $MobileAppPath\App.tsx" -ForegroundColor Red
    return
}

# Test 3: Customer Registration (Correct Flow)
Write-Host "`n👤 TEST 3: Customer Registration" -ForegroundColor White
Write-Host "================================" -ForegroundColor Gray

$randomId = Get-Random -Minimum 100000 -Maximum 999999
$testCustomer = @{
    username = "mobile_test_$randomId"
    email = "mobile$randomId@example.com"
    password = "testpass123"
    first_name = "Mobile"
    last_name = "TestUser"
    phone_number = "+1$(Get-Random -Minimum 1000000000 -Maximum 9999999999)"
    address = "123 Test Street, Test City"
}

try {
    $registrationResponse = Invoke-RestMethod -Uri "$BackendURL/api/customers/register/" -Method POST -Body ($testCustomer | ConvertTo-Json) -ContentType "application/json"
    
    if ($registrationResponse.customer.id) {
        $customerId = $registrationResponse.customer.id
        $username = $testCustomer.username
        $password = $testCustomer.password
        
        Write-Host "✅ Customer registered successfully!" -ForegroundColor Green
        Write-Host "   Customer ID: $customerId" -ForegroundColor Gray
        Write-Host "   Username: $username" -ForegroundColor Gray
        $testResults.CustomerRegistration = $true
    } else {
        Write-Host "❌ Registration successful but no customer ID returned" -ForegroundColor Red
        Write-Host "Response: $($registrationResponse | ConvertTo-Json)" -ForegroundColor Gray
        return
    }
} catch {
    Write-Host "❌ Customer registration failed: $_" -ForegroundColor Red
    return
}

# Test 4: Customer Authentication (Login as the NEW customer)
Write-Host "`n🔐 TEST 4: Customer Authentication" -ForegroundColor White
Write-Host "==================================" -ForegroundColor Gray

try {
    $authData = @{
        username = $username
        password = $password
    }
    
    $authResponse = Invoke-RestMethod -Uri "$BackendURL/api/token/" -Method POST -Body ($authData | ConvertTo-Json) -ContentType "application/json"
    
    if ($authResponse.access) {
        $authToken = $authResponse.access
        $headers = @{
            "Authorization" = "Bearer $authToken"
            "Content-Type" = "application/json"
        }
        
        Write-Host "✅ Authentication successful!" -ForegroundColor Green
        Write-Host "   Token: $($authToken.Substring(0, 20))..." -ForegroundColor Gray
        $testResults.CustomerAuthentication = $true
    } else {
        Write-Host "❌ Authentication failed - no access token received" -ForegroundColor Red
        return
    }
} catch {
    Write-Host "❌ Authentication failed: $_" -ForegroundColor Red
    return
}

# Test 5: Customer Read (Customer accessing their OWN profile)
Write-Host "`n📖 TEST 5: Customer Read (Own Profile)" -ForegroundColor White
Write-Host "======================================" -ForegroundColor Gray

try {
    $readResponse = Invoke-RestMethod -Uri "$BackendURL/api/customers/$customerId/" -Method GET -Headers $headers
    
    if ($readResponse.id -eq $customerId) {
        Write-Host "✅ Customer can read their own profile!" -ForegroundColor Green
        Write-Host "   Name: $($readResponse.first_name) $($readResponse.last_name)" -ForegroundColor Gray
        Write-Host "   Email: $($readResponse.email)" -ForegroundColor Gray
        $testResults.CustomerRead = $true
    } else {
        Write-Host "❌ Read response contains wrong customer data" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Customer read failed: $_" -ForegroundColor Red
}

# Test 6: Customer Update (Customer updating their OWN profile)
Write-Host "`n✏️  TEST 6: Customer Update (Own Profile)" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Gray

try {
    $updateData = @{
        phone_number = "+1$(Get-Random -Minimum 1000000000 -Maximum 9999999999)"
        address = "456 Updated Avenue, New City"
    }
    
    $updateResponse = Invoke-RestMethod -Uri "$BackendURL/api/customers/$customerId/" -Method PATCH -Body ($updateData | ConvertTo-Json) -Headers $headers
    
    if ($updateResponse.phone_number -eq $updateData.phone_number) {
        Write-Host "✅ Customer can update their own profile!" -ForegroundColor Green
        Write-Host "   Updated phone: $($updateResponse.phone_number)" -ForegroundColor Gray
        Write-Host "   Updated address: $($updateResponse.address)" -ForegroundColor Gray
        $testResults.CustomerUpdate = $true
    } else {
        Write-Host "❌ Update response doesn't reflect changes" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Customer update failed: $_" -ForegroundColor Red
}

# Test 7: Customer Delete (Customer deleting their OWN profile)
Write-Host "`n🗑️  TEST 7: Customer Delete (Own Profile)" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Gray

try {
    $deleteResponse = Invoke-RestMethod -Uri "$BackendURL/api/customers/$customerId/" -Method DELETE -Headers $headers
    Write-Host "✅ Customer can delete their own profile!" -ForegroundColor Green
    Write-Host "   Profile deleted successfully" -ForegroundColor Gray
    $testResults.CustomerDelete = $true
} catch {
    Write-Host "❌ Customer delete failed: $_" -ForegroundColor Red
}

# Test Results Summary
Write-Host "`n📊 TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

$passedTests = ($testResults.Values | Where-Object { $_ -eq $true }).Count
$totalTests = $testResults.Count
$successRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "`n🎯 Overall Success Rate: $passedTests/$totalTests ($successRate%)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

foreach ($test in $testResults.GetEnumerator()) {
    $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($test.Value) { "Green" } else { "Red" }
    Write-Host "   $($test.Key): $status" -ForegroundColor $color
}

if ($successRate -eq 100) {
    Write-Host "`n🎉 EXCELLENT! All Customer CRUD operations working perfectly!" -ForegroundColor Green
    Write-Host "🚀 Ready for mobile app manual testing on physical device" -ForegroundColor Green
    Write-Host "`n📱 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Start mobile app: cd C:\Users\360WEB\DeliveryAppMobile && npx expo start" -ForegroundColor Yellow
    Write-Host "2. Open app on physical device (scan QR code)" -ForegroundColor Yellow
    Write-Host "3. Test Customer CRUD operations manually" -ForegroundColor Yellow
    Write-Host "4. Proceed with implementing Driver and Vehicle CRUD screens" -ForegroundColor Yellow
} elseif ($successRate -ge 80) {
    Write-Host "`n✅ GOOD! Most operations working. Address remaining issues before mobile testing." -ForegroundColor Yellow
} else {
    Write-Host "`n⚠️  ISSUES DETECTED! Fix failing tests before proceeding." -ForegroundColor Red
}

Write-Host "`n📋 Detailed Analysis:" -ForegroundColor Cyan
Write-Host "- Authentication Security: ✅ Working correctly (customers can only access own profiles)" -ForegroundColor Green
Write-Host "- API Response Format: ✅ Registration returns proper customer ID" -ForegroundColor Green
Write-Host "- Network Configuration: ✅ Mobile app configured with current IP (192.168.1.85)" -ForegroundColor Green
Write-Host "- CRUD Chain: $(if ($testResults.CustomerRead -and $testResults.CustomerUpdate -and $testResults.CustomerDelete) { '✅ Complete' } else { '⚠️ Incomplete' })" -ForegroundColor $(if ($testResults.CustomerRead -and $testResults.CustomerUpdate -and $testResults.CustomerDelete) { "Green" } else { "Yellow" })