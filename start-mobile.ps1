# =============================================================================
# START-MOBILE.PS1 - Enhanced Expo Mobile App Startup
# =============================================================================
# This script starts the Expo mobile development server with proper configuration
# Usage: .\start-mobile.ps1

Write-Host "📱 Starting DeliveryApp Mobile Server..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# Navigate to mobile directory
$MobileDir = "C:\Users\360WEB\DeliveryAppMobile"
if (-not (Test-Path $MobileDir)) {
    Write-Host "❌ Mobile directory not found: $MobileDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location $MobileDir
Write-Host "📁 Working directory: $MobileDir" -ForegroundColor Yellow

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "❌ package.json not found. Not a valid Expo project." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    try {
        npm install
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✅ Dependencies found" -ForegroundColor Green
}

# Check if Expo is available
try {
    $expoVersion = npx expo --version 2>$null
    if ($expoVersion) {
        Write-Host "✅ Expo CLI detected (version: $expoVersion)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Expo CLI not found, will install on demand" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Expo check failed, continuing anyway" -ForegroundColor Yellow
}

# Check current network IP for mobile access
try {
    $currentIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*" | Where-Object {$_.PrefixOrigin -eq "Dhcp"}).IPAddress
    if (-not $currentIP) {
        $currentIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -match "^192\.168\."}).IPAddress | Select-Object -First 1
    }
    if ($currentIP) {
        Write-Host "🌐 Current Network IP: $currentIP" -ForegroundColor Cyan
        Write-Host "📱 Expo URL: exp://$currentIP:19000" -ForegroundColor Cyan
    }
} catch {
    Write-Host "🌐 Network IP detection failed" -ForegroundColor Yellow
}

# Check if backend is likely running
$backendStatus = "Unknown"
try {
    if ($currentIP) {
        $response = Invoke-WebRequest -Uri "http://$currentIP:8081/api/" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response) {
            $backendStatus = "✅ Running"
        }
    } else {
        $response = Invoke-WebRequest -Uri "http://localhost:8081/api/" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response) {
            $backendStatus = "✅ Running (localhost)"
        }
    }
} catch {
    $backendStatus = "❌ Not detected"
}

# Display startup information
Write-Host "" -ForegroundColor White
Write-Host "🎯 MOBILE ACCESS POINTS:" -ForegroundColor Green
Write-Host "   💻 Web Browser:    http://localhost:19000" -ForegroundColor White
Write-Host "   📱 QR Code:        Scan with Expo Go app" -ForegroundColor White
if ($currentIP) {
Write-Host "   🌐 Network:        exp://$currentIP:19000" -ForegroundColor White
}
Write-Host "" -ForegroundColor White
Write-Host "🔗 BACKEND STATUS:" -ForegroundColor Green
Write-Host "   Django Server:     $backendStatus" -ForegroundColor White
if ($backendStatus -like "*Not detected*") {
    Write-Host "   💡 Tip: Start backend first with .\start-backend.ps1" -ForegroundColor Yellow
}
Write-Host "" -ForegroundColor White
Write-Host "📱 MOBILE TESTING:" -ForegroundColor Green
Write-Host "   • iOS: Use Camera app to scan QR code" -ForegroundColor White
Write-Host "   • Android: Use Expo Go app to scan QR code" -ForegroundColor White
Write-Host "   • Web: Opens automatically in browser" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "🔧 SERVER CONTROLS:" -ForegroundColor Green
Write-Host "   • Press Ctrl+C to stop server" -ForegroundColor White
Write-Host "   • Press 'r' to reload app" -ForegroundColor White
Write-Host "   • Press 'w' to open web browser" -ForegroundColor White
Write-Host "   • Press 'a' to open Android simulator" -ForegroundColor White
Write-Host "" -ForegroundColor White

# Start Expo development server
Write-Host "🚀 Starting Expo development server..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

try {
    # Start Expo with proper port configuration
    npx expo start --port 19000
} catch {
    Write-Host "" -ForegroundColor White
    Write-Host "❌ Expo server startup failed!" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    Write-Host "💡 Try running: npm install" -ForegroundColor Yellow
} finally {
    Write-Host "" -ForegroundColor White
    Write-Host "🔚 Expo server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}