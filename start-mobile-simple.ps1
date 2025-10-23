# =============================================================================
# START-MOBILE-SIMPLE.PS1 - Simple Expo Mobile Server Startup
# =============================================================================

Write-Host "📱 Starting DeliveryApp Mobile Server..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# Navigate to mobile directory
$MobileDir = "C:\Users\360WEB\DeliveryAppMobile"
Set-Location $MobileDir
Write-Host "📁 Working directory: $MobileDir" -ForegroundColor Yellow

# Check if this is a valid Expo project
if (-not (Test-Path "package.json")) {
    Write-Host "❌ package.json not found. Not a valid Expo project." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  Installing dependencies..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "✅ Dependencies found" -ForegroundColor Green
}

# Get network IP
$currentIP = "localhost"
try {
    $networkIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -match "^192\.168\."}).IPAddress | Select-Object -First 1
    if ($networkIP) {
        $currentIP = $networkIP
        Write-Host "✅ Network IP detected: $currentIP" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Using localhost only" -ForegroundColor Yellow
}

# Check if backend is running
$backendStatus = "❌ Not running"
try {
    $response = Invoke-WebRequest -Uri "http://$currentIP:8081/api/" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($response) {
        $backendStatus = "✅ Running"
    }
} catch {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8081/api/" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response) {
            $backendStatus = "✅ Running (localhost)"
        }
    } catch {
        $backendStatus = "❌ Not detected"
    }
}

# Display connection information
Write-Host "" -ForegroundColor White
Write-Host "🎯 ACCESS POINTS:" -ForegroundColor Green
Write-Host "   💻 Web Browser:    http://localhost:19000" -ForegroundColor White
Write-Host "   📱 QR Code:        Scan with Expo Go app" -ForegroundColor White
if ($currentIP -ne "localhost") {
    Write-Host "   🌐 Network:        exp://$currentIP:19000" -ForegroundColor White
}
Write-Host "" -ForegroundColor White
Write-Host "🔗 BACKEND STATUS:" -ForegroundColor Green
Write-Host "   Django Server:     $backendStatus" -ForegroundColor White
if ($backendStatus -like "*Not*") {
    Write-Host "   💡 Start backend: .\start-backend-simple.ps1" -ForegroundColor Yellow
}
Write-Host "" -ForegroundColor White
Write-Host "🔧 CONTROLS:" -ForegroundColor Green
Write-Host "   • Press Ctrl+C to stop server" -ForegroundColor White
Write-Host "   • Press 'r' to reload app" -ForegroundColor White
Write-Host "   • Press 'w' to open web browser" -ForegroundColor White
Write-Host "" -ForegroundColor White

# Start Expo server
Write-Host "🚀 Starting Expo development server..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

try {
    npx expo start --port 19000
} catch {
    Write-Host "" -ForegroundColor White
    Write-Host "❌ Expo server startup failed!" -ForegroundColor Red
} finally {
    Write-Host "" -ForegroundColor White
    Write-Host "🔚 Expo server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}