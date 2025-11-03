# DeliveryApp Backend Startup Script - Fixed Python Path

Write-Host "🚀 DELIVERYAPP BACKEND STARTUP" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Define Python path
$pythonExe = "C:\Users\360WEB\AppData\Local\Programs\Python\Python313\python.exe"

# Verify Python installation
Write-Host "`n🐍 Checking Python installation..." -ForegroundColor Yellow
try {
  $pythonVersion = & $pythonExe --version
  Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
}
catch {
  Write-Host "❌ Python not found at: $pythonExe" -ForegroundColor Red
  exit 1
}

# Get network IP
Write-Host "`n🌐 Detecting network configuration..." -ForegroundColor Yellow
$networkIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" } | Select-Object -First 1).IPAddress
if (!$networkIP) { 
  $networkIP = "127.0.0.1" 
  Write-Host "⚠️ No network IP found, using localhost" -ForegroundColor Yellow
}
else {
  Write-Host "✅ Network IP detected: $networkIP" -ForegroundColor Green
}

# Set location
Write-Host "`n📁 Setting working directory..." -ForegroundColor Yellow
Set-Location "C:\Users\360WEB\DeliveryAppBackend"
Write-Host "✅ Working directory: $(Get-Location)" -ForegroundColor Green

# Check Django project
Write-Host "`n🔧 Checking Django project..." -ForegroundColor Yellow
if (Test-Path "manage.py") {
  Write-Host "✅ Django project found" -ForegroundColor Green
}
else {
  Write-Host "❌ manage.py not found in current directory" -ForegroundColor Red
  exit 1
}

# Run database check
Write-Host "`n📊 Checking database..." -ForegroundColor Yellow
try {
  & $pythonExe manage.py check --verbosity=0
  Write-Host "✅ Database configuration valid" -ForegroundColor Green
}
catch {
  Write-Host "⚠️ Database check failed, continuing..." -ForegroundColor Yellow
}

# Start Django server
Write-Host "`n🚀 Starting Django server..." -ForegroundColor Yellow
Write-Host "   Server will be accessible at:" -ForegroundColor Gray
Write-Host "   - Local: http://127.0.0.1:8081" -ForegroundColor Gray
Write-Host "   - Network: http://$networkIP:8081" -ForegroundColor Gray
Write-Host "`n⚠️ Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Cyan

# Start the server
& $pythonExe manage.py runserver 0.0.0.0:8081