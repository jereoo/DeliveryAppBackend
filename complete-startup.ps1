# Complete Server Startup and Test Script

param(
  [string]$Port = "8000",
  [string]$ServerHost = "127.0.0.1"
)

Write-Host "🚀 DELIVERYAPP - COMPLETE STARTUP & TEST" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Define Python path
$pythonExe = "C:\Users\360WEB\AppData\Local\Programs\Python\Python313\python.exe"

# Stop any existing Python processes
Write-Host "`n🛑 Stopping existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Set location
Set-Location "C:\Users\360WEB\DeliveryAppBackend"

# Start Django server in background
Write-Host "`n🚀 Starting Django server on $ServerHost`:$Port..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock {
  param($pythonPath, $serverHost, $port)
  & $pythonPath manage.py runserver "$serverHost`:$port"
} -ArgumentList $pythonExe, $ServerHost, $Port

# Wait for server to start
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test server connectivity
Write-Host "`n🧪 Testing server connectivity..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0

do {
  $attempt++
  try {
    Invoke-WebRequest -Uri "http://$ServerHost`:$Port/" -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "✅ Server is responding!" -ForegroundColor Green
    break
  }
  catch {
    Write-Host "   Attempt $attempt failed, retrying..." -ForegroundColor Gray
    Start-Sleep -Seconds 1
  }
} while ($attempt -lt $maxAttempts)

if ($attempt -eq $maxAttempts) {
  Write-Host "❌ Server failed to start properly" -ForegroundColor Red
  Stop-Job $serverJob -ErrorAction SilentlyContinue
  Remove-Job $serverJob -ErrorAction SilentlyContinue
  exit 1
}

# Test authentication
Write-Host "`n🔐 Testing authentication..." -ForegroundColor Yellow
$body = @{
  username = "admin"
  password = "w3r3w0lf"
} | ConvertTo-Json

try {
  $response = Invoke-WebRequest -Uri "http://$ServerHost`:$Port/api/token/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $body -TimeoutSec 10
    
  Write-Host "✅ Authentication Success!" -ForegroundColor Green
  $tokenData = $response.Content | ConvertFrom-Json
    
  Write-Host "`n📝 Token Information:" -ForegroundColor Cyan
  Write-Host "Access Token: $($tokenData.access.Substring(0,20))..." -ForegroundColor Gray
  Write-Host "Refresh Token: $($tokenData.refresh.Substring(0,20))..." -ForegroundColor Gray
    
  # Save token
  $tokenData.access | Out-File -FilePath "last-token.txt" -Encoding UTF8
  Write-Host "✅ Token saved to last-token.txt" -ForegroundColor Green
    
  # Test API endpoint
  Write-Host "`n🌐 Testing API endpoints..." -ForegroundColor Yellow
  $headers = @{
    "Authorization" = "Bearer $($tokenData.access)"
    "Content-Type"  = "application/json"
  }
    
  try {
    $apiResponse = Invoke-WebRequest -Uri "http://$ServerHost`:$Port/api/deliveries/" -Headers $headers -TimeoutSec 10
    Write-Host "✅ API endpoint accessible!" -ForegroundColor Green
    Write-Host "Status: $($apiResponse.StatusCode)" -ForegroundColor Gray
  }
  catch {
    Write-Host "⚠️ API endpoint test failed: $($_.Exception.Message)" -ForegroundColor Yellow
  }
    
}
catch {
  Write-Host "❌ Authentication Failed!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Display server info
Write-Host "`n🌐 Server Information:" -ForegroundColor Cyan
Write-Host "Local URL: http://$ServerHost`:$Port" -ForegroundColor Gray
Write-Host "Network URL: http://$(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like '192.168.*' } | Select-Object -First 1 -ExpandProperty IPAddress):$Port" -ForegroundColor Gray

Write-Host "`n⚠️ Server is running in background. Use 'Stop-Job' commands to stop it." -ForegroundColor Yellow
Write-Host "Job ID: $($serverJob.Id)" -ForegroundColor Gray

# Update mobile app configuration
Write-Host "`n📱 Updating mobile app configuration..." -ForegroundColor Yellow
$networkIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" } | Select-Object -First 1).IPAddress
if ($networkIP) {
  $mobileConfigPath = "C:\Users\360WEB\DeliveryAppMobile\NetworkConfig_Enhanced.js"
  if (Test-Path $mobileConfigPath) {
    $newEndpoint = "http://$networkIP`:$Port"
    Write-Host "✅ Mobile app should connect to: $newEndpoint" -ForegroundColor Green
  }
}

Write-Host "`n🎉 STARTUP COMPLETE!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan