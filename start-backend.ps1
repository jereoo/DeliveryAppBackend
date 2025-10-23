# =============================================================================
# START-BACKEND.PS1 - Enhanced Django Server Startup
# =============================================================================
# This script starts the Django backend server with proper configuration
# Usage: .\start-backend.ps1

Write-Host "🚚 Starting DeliveryApp Backend Server..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

# Navigate to backend directory
$BackendDir = "C:\Users\360WEB\DeliveryAppBackend"
if (-not (Test-Path $BackendDir)) {
    Write-Host "❌ Backend directory not found: $BackendDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location $BackendDir
Write-Host "📁 Working directory: $BackendDir" -ForegroundColor Yellow

# Set execution policy for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Django is installed
try {
    $djangoVersion = python -c "import django; print(django.get_version())" 2>$null
    if ($djangoVersion) {
        Write-Host "✅ Django $djangoVersion detected" -ForegroundColor Green
    } else {
        throw "Django not found"
    }
} catch {
    Write-Host "❌ Django not installed in virtual environment" -ForegroundColor Red
    Write-Host "💡 Run: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if database is ready
Write-Host "🔍 Checking database connection..." -ForegroundColor Yellow
try {
    python manage.py check --database default 2>$null
    Write-Host "✅ Database connection verified" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Database check failed - continuing anyway" -ForegroundColor Yellow
}

# Get current IP for network info
$currentIP = $null
try {
    $currentIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*" | Where-Object {$_.PrefixOrigin -eq "Dhcp"}).IPAddress
    if (-not $currentIP) {
        $currentIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -match "^192\.168\."}).IPAddress | Select-Object -First 1
    }
    if ($currentIP) {
        Write-Host "🌐 Current Network IP: $currentIP" -ForegroundColor Cyan
        Write-Host "📱 Mobile access: http://$currentIP:8081/admin/" -ForegroundColor Cyan
    }
} catch {
    Write-Host "🌐 Network IP detection failed" -ForegroundColor Yellow
}

# Display startup information
Write-Host "" -ForegroundColor White
Write-Host "🎯 SERVER ENDPOINTS:" -ForegroundColor Green
Write-Host "   💻 Local Admin:    http://localhost:8081/admin/" -ForegroundColor White
Write-Host "   📚 API Root:       http://localhost:8081/api/" -ForegroundColor White
if ($currentIP) {
    Write-Host "   📱 Mobile Access:  http://$currentIP:8081/" -ForegroundColor White
}
Write-Host "" -ForegroundColor White
Write-Host "🔧 SERVER CONTROLS:" -ForegroundColor Green
Write-Host "   • Press Ctrl+C to stop server" -ForegroundColor White
Write-Host "   • Server will auto-reload on file changes" -ForegroundColor White
Write-Host "" -ForegroundColor White

# Start Django development server
Write-Host "🚀 Starting Django development server..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

try {
    # Use the full Python path to ensure we're using the venv
    & ".\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8081
} catch {
    Write-Host "" -ForegroundColor White
    Write-Host "❌ Server startup failed!" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
} finally {
    Write-Host "" -ForegroundColor White
    Write-Host "🔚 Django server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}