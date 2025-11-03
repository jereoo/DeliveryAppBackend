# 🔧 Fix Network Login Issue - Automated Diagnostic Script

Write-Host "🔍 DIAGNOSING NETWORK LOGIN ISSUE" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Get current network configuration
Write-Host "📍 Current Network Configuration:" -ForegroundColor Yellow
ipconfig | findstr "IPv4"

# Test backend connectivity
Write-Host "🌐 Testing Backend Connectivity:" -ForegroundColor Yellow
$backendUrls = @(
  "http://192.168.1.77:8081",
  "http://192.168.1.85:8081", 
  "http://192.168.1.87:8081",
  "http://172.20.10.6:8081"
)

foreach ($url in $backendUrls) {
  try {
    $response = Invoke-WebRequest -Uri "$url/api/customers/" -Method GET -TimeoutSec 5
    Write-Host "✅ $url - ACCESSIBLE" -ForegroundColor Green
    break
  }
  catch {
    Write-Host "❌ $url - NOT ACCESSIBLE" -ForegroundColor Red
  }
}

# Check if backend is running
Write-Host "🚀 Checking Django Backend:" -ForegroundColor Yellow
$process = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($process) {
  Write-Host "✅ Django backend process found" -ForegroundColor Green
}
else {
  Write-Host "⚠️ Django backend not running - starting now..." -ForegroundColor Yellow
  Start-Process powershell -ArgumentList "-Command", "cd 'C:\Users\360WEB\DeliveryAppBackend'; .\start-django.ps1"
  Start-Sleep 10
}

# Test authentication endpoint
Write-Host "🔐 Testing Authentication Endpoint:" -ForegroundColor Yellow
try {
  $authResponse = Invoke-WebRequest -Uri "http://192.168.1.77:8081/api/token/" -Method GET -TimeoutSec 5
  Write-Host "✅ Auth endpoint accessible" -ForegroundColor Green
}
catch {
  Write-Host "❌ Auth endpoint not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check mobile app network configuration in App.tsx" -ForegroundColor White
Write-Host "2. Verify API_BASE URL matches accessible backend" -ForegroundColor White
Write-Host "3. Test login with known credentials" -ForegroundColor White