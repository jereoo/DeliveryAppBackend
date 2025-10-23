# =============================================================================
# CHECK-STATUS.PS1 - Server Status Checker
# =============================================================================
# This script checks if both servers are running and provides connection info

Write-Host "🔍 DeliveryApp - Server Status Check" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan

# Get current IP
$currentIP = $null
try {
    $currentIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*" | Where-Object {$_.PrefixOrigin -eq "Dhcp"}).IPAddress
    if (-not $currentIP) {
        $currentIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -match "^192\.168\."}).IPAddress | Select-Object -First 1
    }
} catch {
    $currentIP = "Unknown"
}

Write-Host "🌐 Current Network IP: $currentIP" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White

# Check Django Backend
Write-Host "🚚 DJANGO BACKEND SERVER:" -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8081/api/" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   Status: ✅ RUNNING" -ForegroundColor Green
    Write-Host "   Local:  http://localhost:8081/admin/" -ForegroundColor White
    if ($currentIP -ne "Unknown") {
        Write-Host "   Mobile: http://$currentIP:8081/admin/" -ForegroundColor White
    }
} catch {
    Write-Host "   Status: ❌ NOT RUNNING" -ForegroundColor Red
    Write-Host "   Start:  .\start-backend.ps1" -ForegroundColor Yellow
}

Write-Host "" -ForegroundColor White

# Check Expo Mobile Server
Write-Host "📱 EXPO MOBILE SERVER:" -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:19000" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   Status: ✅ RUNNING" -ForegroundColor Green
    Write-Host "   Web:    http://localhost:19000" -ForegroundColor White
    if ($currentIP -ne "Unknown") {
        Write-Host "   Mobile: exp://$currentIP:19000" -ForegroundColor White
    }
} catch {
    Write-Host "   Status: ❌ NOT RUNNING" -ForegroundColor Red
    Write-Host "   Start:  .\start-mobile.ps1" -ForegroundColor Yellow
}

Write-Host "" -ForegroundColor White

# Check processes
Write-Host "🔍 RUNNING PROCESSES:" -ForegroundColor Green
$djangoProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*manage.py*runserver*"}
$nodeProcess = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*expo*"}

if ($djangoProcess) {
    Write-Host "   Django: ✅ Process found (PID: $($djangoProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "   Django: ❌ No process found" -ForegroundColor Red
}

if ($nodeProcess) {
    Write-Host "   Expo:   ✅ Process found (PID: $($nodeProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "   Expo:   ❌ No process found" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "🚀 QUICK START OPTIONS:" -ForegroundColor Green
Write-Host "   Both servers:    .\start-all.ps1" -ForegroundColor White
Write-Host "   Backend only:    .\start-backend.ps1" -ForegroundColor White
Write-Host "   Mobile only:     .\start-mobile.ps1" -ForegroundColor White

Read-Host "`nPress Enter to exit"