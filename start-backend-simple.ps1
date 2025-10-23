# =============================================================================
# START-BACKEND.PS1 - Simple Django Server Startup
# =============================================================================

Write-Host "🚚 Starting DeliveryApp Backend Server..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

# Navigate to backend directory
$BackendDir = "C:\Users\360WEB\DeliveryAppBackend"
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

# Check Django installation
Write-Host "🔍 Checking Django installation..." -ForegroundColor Yellow
try {
    $djangoVersion = & ".\venv\Scripts\python.exe" -c "import django; print(django.get_version())" 2>$null
    if ($djangoVersion) {
        Write-Host "✅ Django $djangoVersion detected" -ForegroundColor Green
    } else {
        Write-Host "❌ Django not found" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Django check failed" -ForegroundColor Red
    exit 1
}

# Get network IP
Write-Host "🌐 Detecting network configuration..." -ForegroundColor Yellow
$currentIP = "localhost"
try {
    $networkIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -match "^192\.168\."}).IPAddress | Select-Object -First 1
    if ($networkIP) {
        $currentIP = $networkIP
        Write-Host "✅ Network IP detected: $currentIP" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Using localhost only" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Using localhost only" -ForegroundColor Yellow
}

# Display connection information
Write-Host "" -ForegroundColor White
Write-Host "🎯 CONNECTION DETAILS:" -ForegroundColor Green
Write-Host "   💻 Admin Panel:    http://localhost:8081/admin/" -ForegroundColor White
Write-Host "   📚 API Root:       http://localhost:8081/api/" -ForegroundColor White
if ($currentIP -ne "localhost") {
    Write-Host "   📱 Mobile Access:  http://$currentIP:8081/" -ForegroundColor White
}
Write-Host "" -ForegroundColor White
Write-Host "🔧 CONTROLS:" -ForegroundColor Green
Write-Host "   • Press Ctrl+C to stop server" -ForegroundColor White
Write-Host "   • Server auto-reloads on file changes" -ForegroundColor White
Write-Host "" -ForegroundColor White

# Start Django server
Write-Host "🚀 Starting Django development server..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

try {
    & ".\venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8081
} catch {
    Write-Host "" -ForegroundColor White
    Write-Host "❌ Server startup failed!" -ForegroundColor Red
} finally {
    Write-Host "" -ForegroundColor White
    Write-Host "🔚 Django server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}