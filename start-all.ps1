# =============================================================================
# START-ALL.PS1 - Master Startup Script for DeliveryApp
# =============================================================================
# This script starts both Django backend and Expo mobile servers
# Usage: .\start-all.ps1

param(
    [switch]$BackendOnly,
    [switch]$MobileOnly,
    [switch]$Sequential
)

Write-Host "🚚📱 DeliveryApp - Master Startup Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

# Set execution policy for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

if ($BackendOnly) {
    Write-Host "🚚 Starting Backend Only..." -ForegroundColor Yellow
    & ".\start-backend.ps1"
    exit
}

if ($MobileOnly) {
    Write-Host "📱 Starting Mobile Only..." -ForegroundColor Yellow
    & ".\start-mobile.ps1"
    exit
}

if ($Sequential) {
    Write-Host "🔄 Sequential Mode: Starting Backend first, then Mobile..." -ForegroundColor Yellow
    Write-Host "Step 1: Starting Backend Server..." -ForegroundColor Cyan
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "& '.\start-backend.ps1'"
    
    Start-Sleep -Seconds 5
    Write-Host "Step 2: Starting Mobile Server..." -ForegroundColor Cyan
    & ".\start-mobile.ps1"
    exit
}

# Default: Start both servers in parallel
Write-Host "🚀 Parallel Mode: Starting both Backend and Mobile servers..." -ForegroundColor Yellow
Write-Host "" -ForegroundColor White

# Start backend server in new window
Write-Host "🚚 Launching Backend Server..." -ForegroundColor Green
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "& '.\start-backend.ps1'"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start mobile server in current window
Write-Host "📱 Launching Mobile Server..." -ForegroundColor Green
Write-Host "" -ForegroundColor White

# Provide instructions
Write-Host "📋 STARTUP INFORMATION:" -ForegroundColor Green
Write-Host "   • Backend server: Started in separate window" -ForegroundColor White
Write-Host "   • Mobile server: Starting in this window" -ForegroundColor White
Write-Host "   • Both servers will run simultaneously" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "💡 USAGE TIPS:" -ForegroundColor Green
Write-Host "   • Backend only:  .\start-all.ps1 -BackendOnly" -ForegroundColor White
Write-Host "   • Mobile only:   .\start-all.ps1 -MobileOnly" -ForegroundColor White
Write-Host "   • Sequential:    .\start-all.ps1 -Sequential" -ForegroundColor White
Write-Host "" -ForegroundColor White

Start-Sleep -Seconds 2

# Start mobile server
& ".\start-mobile.ps1"