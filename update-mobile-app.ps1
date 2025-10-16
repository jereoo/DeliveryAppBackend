# 🚚 DeliveryApp Mobile - App.tsx Update Script
# This script copies the keyboard-fixed version to your mobile app directory

Write-Host "🚚 DeliveryApp Mobile - App.tsx Update Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Define paths
$sourceFile = "C:\Users\360WEB\DeliveryAppBackend\mobile\App-KeyboardFixed.tsx"
$targetDir = "C:\Users\360WEB\DeliveryAppMobile"
$targetFile = "$targetDir\App.tsx"

# Check if source file exists
if (-Not (Test-Path $sourceFile)) {
    Write-Host "❌ ERROR: Source file not found: $sourceFile" -ForegroundColor Red
    Write-Host "   Please make sure the keyboard-fixed version exists." -ForegroundColor Yellow
    exit 1
}

# Check if target directory exists
if (-Not (Test-Path $targetDir)) {
    Write-Host "❌ ERROR: Target directory not found: $targetDir" -ForegroundColor Red
    Write-Host "   Please make sure your DeliveryAppMobile directory exists." -ForegroundColor Yellow
    exit 1
}

# Backup existing App.tsx if it exists
if (Test-Path $targetFile) {
    $backupFile = "$targetDir\App.tsx.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "📋 Backing up existing App.tsx to: $backupFile" -ForegroundColor Yellow
    Copy-Item $targetFile $backupFile
}

# Copy the keyboard-fixed version
Write-Host "📁 Copying keyboard-fixed version..." -ForegroundColor Green
try {
    Copy-Item $sourceFile $targetFile -Force
    Write-Host "✅ SUCCESS: App.tsx updated with keyboard fix!" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Failed to copy file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Display next steps
Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Restart Expo server: npx expo start --port 19000" -ForegroundColor White
Write-Host "2. Test customer registration on your phone" -ForegroundColor White
Write-Host "3. The keyboard should no longer block bottom fields" -ForegroundColor White

Write-Host ""
Write-Host "🔧 WHAT WAS FIXED:" -ForegroundColor Cyan
Write-Host "✅ Added KeyboardAvoidingView for both iOS and Android" -ForegroundColor Green
Write-Host "✅ Added proper scroll handling with keyboardShouldPersistTaps" -ForegroundColor Green
Write-Host "✅ Added extra padding to ensure buttons stay visible" -ForegroundColor Green
Write-Host "✅ Fixed customer and driver registration forms" -ForegroundColor Green

Write-Host ""
Write-Host "📱 TEST INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "1. Open mobile app on your phone" -ForegroundColor White
Write-Host "2. Go to 'Register as Customer'" -ForegroundColor White
Write-Host "3. Fill in the form fields from top to bottom" -ForegroundColor White
Write-Host "4. When keyboard appears, scroll down to access bottom fields" -ForegroundColor White
Write-Host "5. Register button should now be visible above keyboard" -ForegroundColor White

Write-Host ""
Write-Host "🚀 App.tsx update complete! Ready for testing." -ForegroundColor Green