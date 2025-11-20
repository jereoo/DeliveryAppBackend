# Test API endpoints on localhost
$baseUrl = "http://127.0.0.1:8081"
$headers = @{ 'Content-Type' = 'application/json' }

Write-Host "=== TESTING API ON LOCALHOST ===" -ForegroundColor Green

# Test 1: Health Check
Write-Host "1. HEALTH CHECK" -ForegroundColor Cyan
try {
  $healthResponse = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
  Write-Host "✅ Health check successful!" -ForegroundColor Green
  Write-Host "   Message: $($healthResponse.message)" -ForegroundColor Gray
}
catch {
  Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Authentication
Write-Host "2. AUTHENTICATION TEST" -ForegroundColor Cyan
$authData = @{
  username = "admin"
  password = "admin123"
} | ConvertTo-Json

try {
  $tokenResponse = Invoke-RestMethod -Uri "$baseUrl/api/token/" -Method POST -Body $authData -Headers $headers
  Write-Host "✅ Authentication successful!" -ForegroundColor Green
  Write-Host "   Access Token: $($tokenResponse.access.Substring(0,30))..." -ForegroundColor Gray
    
  # Save token for mobile app
  $tokenResponse.access | Out-File "last-token.txt" -NoNewline
    
  # Set up authenticated headers
  $authHeaders = @{
    'Content-Type'  = 'application/json'
    'Authorization' = "Bearer $($tokenResponse.access)"
  }
    
  Write-Host ""
    
  # Test 3: API Root
  Write-Host "3. API ROOT TEST" -ForegroundColor Cyan
  try {
    $apiRoot = Invoke-RestMethod -Uri "$baseUrl/api/" -Method GET -Headers $authHeaders
    Write-Host "✅ API root accessible" -ForegroundColor Green
  }
  catch {
    Write-Host "❌ API root failed: $($_.Exception.Message)" -ForegroundColor Red
  }
    
}
catch {
  Write-Host "❌ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== LOCALHOST API TEST COMPLETE ===" -ForegroundColor Green