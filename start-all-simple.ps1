# =============================================================================
# START-ALL-SIMPLE.PS1 - Simple Master Startup Script
# =============================================================================

param(
    [switch]$BackendOnly,
    [switch]$MobileOnly
)

Write-Host "🚚📱 DeliveryApp - Simple Startup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan

if ($BackendOnly) {
    Write-Host "🚚 Starting Backend Only..." -ForegroundColor Yellow
    & ".\start-backend-simple.ps1"
    exit
}

if ($MobileOnly) {
    Write-Host "📱 Starting Mobile Only..." -ForegroundColor Yellow
    & ".\start-mobile-simple.ps1"
    exit
}

# Start both servers
Write-Host "🚀 Starting both servers..." -ForegroundColor Yellow
Write-Host "Backend will start in a new window" -ForegroundColor Cyan
Write-Host "Mobile will start in this window" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White

# Start backend in new window
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "& '.\start-backend-simple.ps1'"

# Wait a moment
Start-Sleep -Seconds 3

# Start mobile in current window
& ".\start-mobile-simple.ps1"