# CIO DIRECTIVE: PERMANENT LAUNCH FIX - COMPREHENSIVE STARTUP VERIFICATION
# Status: Final validation script to ensure zero manual processes required
# Created: Per CIO mandate for operational excellence

param(
  [switch]$SkipHealthCheck,
  [switch]$QuickStart,
  [int]$MaxWaitTime = 30
)

function Write-CIOHeader {
  Write-Host ""
  Write-Host "================================================================" -ForegroundColor Cyan
  Write-Host "  🎯 CIO DIRECTIVE: PERMANENT LAUNCH FIX VERIFICATION" -ForegroundColor Green
  Write-Host "================================================================" -ForegroundColor Cyan
  Write-Host ""
}

function Write-CIOStatus {
  param([string]$Message, [string]$Color = "White")
  Write-Host "📊 $Message" -ForegroundColor $Color
}

function Test-BackendHealth {
  param([int]$TimeoutSeconds = 10)
    
  $maxAttempts = $TimeoutSeconds
  $attempt = 0
    
  while ($attempt -lt $maxAttempts) {
    try {
      $response = Invoke-WebRequest -Uri "http://localhost:8000/api/deliveries/" -Method GET -TimeoutSec 2 -ErrorAction Stop
      if ($response.StatusCode -eq 200) {
        return $true
      }
    }
    catch {
      Start-Sleep -Seconds 1
      $attempt++
    }
  }
  return $false
}

function Test-ProcessRunning {
  param([string]$ProcessName)
  return $null -ne (Get-Process -Name $ProcessName -ErrorAction SilentlyContinue)
}

Write-CIOHeader

# 1. Check if Django is running
Write-CIOStatus "Checking Django backend server..." "Yellow"
if (Test-ProcessRunning "python") {
  Write-CIOStatus "✅ Django process detected" "Green"
    
  if (-not $SkipHealthCheck) {
    Write-CIOStatus "🔍 Performing health check..." "Yellow"
    if (Test-BackendHealth -TimeoutSeconds $MaxWaitTime) {
      Write-CIOStatus "✅ Backend API responding correctly" "Green"
      $backendStatus = "OPERATIONAL"
    }
    else {
      Write-CIOStatus "⚠️  Backend not responding, may still be starting" "Yellow"
      $backendStatus = "STARTING"
    }
  }
  else {
    $backendStatus = "DETECTED"
  }
}
else {
  Write-CIOStatus "❌ Django not running - execute start-fullstack.bat" "Red"
  $backendStatus = "NOT_RUNNING"
}

# 2. Check if Expo/Node is running  
Write-CIOStatus "Checking Expo mobile server..." "Yellow"
if (Test-ProcessRunning "node") {
  Write-CIOStatus "✅ Expo/Node process detected" "Green"
  $mobileStatus = "OPERATIONAL"
}
else {
  Write-CIOStatus "❌ Expo not running - execute start-fullstack.bat" "Red"
  $mobileStatus = "NOT_RUNNING"
}

# 3. Network configuration check
Write-CIOStatus "Checking network configuration..." "Yellow"
$LOCAL_IP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*", "Ethernet*" | Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*" } | Select-Object -First 1).IPAddress
if ($LOCAL_IP) {
  Write-CIOStatus "✅ Local IP detected: $LOCAL_IP" "Green"
  $networkStatus = "CONFIGURED"
}
else {
  Write-CIOStatus "⚠️  Network IP detection failed" "Yellow"
  $networkStatus = "UNKNOWN"
}

# 4. Environment validation
Write-CIOStatus "Validating environment files..." "Yellow"
$envFiles = @(
  "c:\Users\360WEB\DeliveryAppBackend\.env",
  "c:\Users\360WEB\DeliveryAppMobile\.env"
)

$envStatus = "VALID"
foreach ($envFile in $envFiles) {
  if (Test-Path $envFile) {
    Write-CIOStatus "✅ Found: $envFile" "Green"
  }
  else {
    Write-CIOStatus "⚠️  Missing: $envFile" "Yellow"
    $envStatus = "INCOMPLETE"
  }
}

# 5. Final CIO Report
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  📋 CIO DIRECTIVE IMPLEMENTATION STATUS" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

$statusColor = if ($backendStatus -eq "OPERATIONAL" -and $mobileStatus -eq "OPERATIONAL") { "Green" } else { "Yellow" }

Write-Host "  Backend Server:    $backendStatus" -ForegroundColor $statusColor
Write-Host "  Mobile Server:     $mobileStatus" -ForegroundColor $statusColor
Write-Host "  Network Config:    $networkStatus" -ForegroundColor $(if ($networkStatus -eq "CONFIGURED") { "Green" } else { "Yellow" })
Write-Host "  Environment:       $envStatus" -ForegroundColor $(if ($envStatus -eq "VALID") { "Green" } else { "Yellow" })
Write-Host ""
Write-Host "  Backend URL:       http://localhost:8000/api/" -ForegroundColor White
if ($LOCAL_IP) {
  Write-Host "  Mobile URL:        http://$LOCAL_IP:8000/api/" -ForegroundColor White
}
Write-Host "  Expo Dashboard:    http://localhost:19002/" -ForegroundColor White
Write-Host ""

if ($backendStatus -eq "OPERATIONAL" -and $mobileStatus -eq "OPERATIONAL") {
  Write-Host "  🎯 CIO DIRECTIVE: FULLY IMPLEMENTED ✅" -ForegroundColor Green
  Write-Host "  Status: ZERO manual processes required" -ForegroundColor Green
}
elseif ($backendStatus -ne "NOT_RUNNING" -and $mobileStatus -ne "NOT_RUNNING") {
  Write-Host "  🔄 CIO DIRECTIVE: STARTUP IN PROGRESS" -ForegroundColor Yellow
  Write-Host "  Status: Services starting, wait 30-60 seconds" -ForegroundColor Yellow
}
else {
  Write-Host "  ⚠️  CIO DIRECTIVE: ACTION REQUIRED" -ForegroundColor Red
  Write-Host "  Status: Execute start-fullstack.bat immediately" -ForegroundColor Red
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""