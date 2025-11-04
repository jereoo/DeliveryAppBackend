# 🧪 Comprehensive Mobile CRUD Testing Automation

Write-Host "🧪 COMPREHENSIVE MOBILE CRUD TESTING" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$TestResults = @()

function Test-APIEndpoint {
  param($url, $method, $body, $token, $testName)
    
  try {
    $headers = @{
      'Content-Type' = 'application/json'
    }
    if ($token) {
      $headers['Authorization'] = "Bearer $token"
    }
        
    $params = @{
      Uri        = $url
      Method     = $method
      Headers    = $headers
      TimeoutSec = 10
    }
        
    if ($body) {
      $params['Body'] = $body
    }
        
    $response = Invoke-RestMethod @params
    Write-Host "✅ $testName - PASS" -ForegroundColor Green
    return @{ Status = "PASS"; Response = $response; Error = $null }
  }
  catch {
    Write-Host "❌ $testName - FAIL: $($_.Exception.Message)" -ForegroundColor Red
    return @{ Status = "FAIL"; Response = $null; Error = $_.Exception.Message }
  }
}

# 1. Test Backend Connectivity
Write-Host "`n🔗 1. BACKEND CONNECTIVITY TESTS" -ForegroundColor Yellow
$baseUrl = "http://192.168.1.77:8081"
$connectTest = Test-APIEndpoint "$baseUrl/api/customers/" "GET" $null $null "Backend Connection"
$TestResults += @{ Test = "Backend Connection"; Result = $connectTest.Status }

# 2. Test Customer Registration
Write-Host "`n👤 2. CUSTOMER REGISTRATION TESTS" -ForegroundColor Yellow
$customerData = @{
  username      = "testuser$(Get-Random)"
  password      = "testpass123"
  email         = "test@example.com"
  first_name    = "Test"
  last_name     = "User"
  address       = "123 Test St"
  phone         = "555-0123"
  customer_type = "individual"
} | ConvertTo-Json

$regTest = Test-APIEndpoint "$baseUrl/api/customers/register/" "POST" $customerData $null "Customer Registration"
$TestResults += @{ Test = "Customer Registration"; Result = $regTest.Status }

# 3. Test Authentication
Write-Host "`n🔐 3. AUTHENTICATION TESTS" -ForegroundColor Yellow
if ($regTest.Status -eq "PASS") {
  $loginData = @{
    username = ($customerData | ConvertFrom-Json).username
    password = ($customerData | ConvertFrom-Json).password
  } | ConvertTo-Json
    
  $authTest = Test-APIEndpoint "$baseUrl/api/token/" "POST" $loginData $null "Authentication"
  $TestResults += @{ Test = "Authentication"; Result = $authTest.Status }
    
  if ($authTest.Status -eq "PASS") {
    $token = $authTest.Response.access
        
    # 4. Test CRUD Operations
    Write-Host "`n✏️ 4. CRUD OPERATION TESTS" -ForegroundColor Yellow
        
    # Test READ (own profile)
    $readTest = Test-APIEndpoint "$baseUrl/api/customers/me/" "GET" $null $token "Customer Profile Read"
    $TestResults += @{ Test = "Profile Read"; Result = $readTest.Status }
        
    # Test UPDATE (own profile)  
    $updateData = @{
      first_name = "Updated"
      last_name  = "Name"
      address    = "456 Updated St"
    } | ConvertTo-Json
        
    $updateTest = Test-APIEndpoint "$baseUrl/api/customers/me/" "PUT" $updateData $token "Customer Profile Update"
    $TestResults += @{ Test = "Profile Update"; Result = $updateTest.Status }
        
    # 5. Test Driver Operations
    Write-Host "`n🚚 5. DRIVER OPERATION TESTS" -ForegroundColor Yellow
    $driversTest = Test-APIEndpoint "$baseUrl/api/drivers/" "GET" $null $token "Drivers List"
    $TestResults += @{ Test = "Drivers List"; Result = $driversTest.Status }
        
    # 6. Test Vehicle Operations
    Write-Host "`n🚛 6. VEHICLE OPERATION TESTS" -ForegroundColor Yellow
    $vehiclesTest = Test-APIEndpoint "$baseUrl/api/vehicles/" "GET" $null $token "Vehicles List"
    $TestResults += @{ Test = "Vehicles List"; Result = $vehiclesTest.Status }
        
    # 7. Test Delivery Operations
    Write-Host "`n📦 7. DELIVERY OPERATION TESTS" -ForegroundColor Yellow
    $deliveriesTest = Test-APIEndpoint "$baseUrl/api/deliveries/" "GET" $null $token "Deliveries List"
    $TestResults += @{ Test = "Deliveries List"; Result = $deliveriesTest.Status }
  }
}

# Summary Report
Write-Host "`n📊 TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

$passCount = ($TestResults | Where-Object { $_.Result -eq "PASS" }).Count
$totalCount = $TestResults.Count
$successRate = [math]::Round(($passCount / $totalCount) * 100, 1)

foreach ($result in $TestResults) {
  $color = if ($result.Result -eq "PASS") { "Green" } else { "Red" }
  Write-Host "$($result.Result.PadRight(4)) - $($result.Test)" -ForegroundColor $color
}

Write-Host "`n🎯 Overall Success Rate: $successRate% ($passCount/$totalCount)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Red" })

# Generate Report File
$reportPath = "test-results-$(Get-Date -Format 'yyyy-MM-dd-HHmm').txt"
$TestResults | Out-File $reportPath
Write-Host "📄 Detailed report saved to: $reportPath" -ForegroundColor Gray