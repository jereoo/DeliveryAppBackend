# 🚚 Update Mobile App with Vehicle Registration
# This script copies the driver+vehicle registration version to your mobile app

Write-Host "🚚 Updating Mobile App with Vehicle Registration" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

$sourceFile = "C:\Users\360WEB\DeliveryAppBackend\OLD_mobile\App-KeyboardFixed.tsx"
$targetFile = "C:\Users\360WEB\DeliveryAppMobile\App.tsx"

# Check if source file exists
if (-Not (Test-Path $sourceFile)) {
    Write-Host "❌ ERROR: Source file not found: $sourceFile" -ForegroundColor Red
    exit 1
}

# Backup existing App.tsx
if (Test-Path $targetFile) {
    $backupFile = "C:\Users\360WEB\DeliveryAppMobile\App.tsx.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "📋 Backing up existing App.tsx to: $(Split-Path $backupFile -Leaf)" -ForegroundColor Yellow
    Copy-Item $targetFile $backupFile
}

# Copy the updated version
Write-Host "📁 Copying updated driver+vehicle registration version..." -ForegroundColor Green
Copy-Item $sourceFile $targetFile -Force

Write-Host ""
Write-Host "✅ SUCCESS: App.tsx updated with vehicle registration!" -ForegroundColor Green

Write-Host ""
Write-Host "🆕 NEW FEATURES ADDED:" -ForegroundColor Cyan
Write-Host "✅ Vehicle License Plate field" -ForegroundColor Green
Write-Host "✅ Vehicle Model field" -ForegroundColor Green  
Write-Host "✅ Vehicle Capacity field (kg)" -ForegroundColor Green
Write-Host "✅ Complete driver+vehicle registration API call" -ForegroundColor Green
Write-Host "✅ Form validation for all required fields" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 TESTING:" -ForegroundColor Cyan
Write-Host "1. Expo server should auto-reload (if not, press 'r')" -ForegroundColor White
Write-Host "2. Go to 'Register as Driver' on your phone" -ForegroundColor White
Write-Host "3. Fill in ALL fields including vehicle information" -ForegroundColor White
Write-Host "4. Click 'Register Driver & Vehicle' button" -ForegroundColor White
Write-Host "5. Should successfully register and redirect to login" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Vehicle registration feature added! Ready for testing." -ForegroundColor Green