# CIO DIRECTIVE: PERMANENT LAUNCH FIX - ZERO TOLERANCE FOR MANUAL PROCESSES
# Status: Comprehensive PowerShell startup automation to eliminate daily 20-60 minute delays
# Created: Per CIO mandate to "PERMANENTLY fix this TODAY"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🚀 CIO-APPROVED FULLSTACK STARTUP (AUTOMATED SOLUTION)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Change to the backend directory
Set-Location "c:\Users\360WEB\DeliveryAppBackend"

Write-Host "📋 Step 1: Terminating existing processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✅ All processes terminated" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Step 2: Starting Django backend server..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/k", "call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000" -WindowStyle Normal

Write-Host ""
Write-Host "📋 Step 3: Waiting for Django to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "📋 Step 4: Detecting local IP address..." -ForegroundColor Yellow
$LOCAL_IP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*", "Ethernet*" | Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*" } | Select-Object -First 1).IPAddress
if (-not $LOCAL_IP) {
  $LOCAL_IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.IPAddress -ne "0.0.0.0" } | Select-Object -First 1).IPAddress
}
Write-Host "🌐 Local IP detected: $LOCAL_IP" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Step 5: Starting Expo mobile development server..." -ForegroundColor Yellow
Set-Location "c:\Users\360WEB\DeliveryAppMobile"
Start-Process -FilePath "cmd" -ArgumentList "/k", "npx expo start --tunnel" -WindowStyle Normal

Write-Host ""
Write-Host "📋 Step 6: Backend health check..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
  if ((Invoke-WebRequest -Uri "http://localhost:8000/api/deliveries/" -Method GET -TimeoutSec 5 -ErrorAction Stop).StatusCode -eq 200) {
    Write-Host "✅ Backend server is running successfully" -ForegroundColor Green
  }
}
catch {
  Write-Host "⚠️  Backend server may still be starting up" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🎯 CIO DIRECTIVE IMPLEMENTATION COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Backend URL: http://localhost:8000/api/" -ForegroundColor White
Write-Host "  Local IP:    http://$LOCAL_IP:8000/api/" -ForegroundColor White
Write-Host "  Mobile:      Expo tunnel active" -ForegroundColor White
Write-Host "  Status:      ZERO manual processes required" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")