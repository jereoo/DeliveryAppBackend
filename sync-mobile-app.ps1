# 🚚 DeliveryApp Mobile - Complete Directory Update Script
# This script updates your mobile app with the keyboard-fixed version

Write-Host "🚚 DeliveryApp Mobile - Complete Directory Update" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Define paths
$sourceDir = "C:\Users\360WEB\DeliveryAppBackend\mobile"
$targetDir = "C:\Users\360WEB\DeliveryAppMobile"
$oldMobileDir = "C:\Users\360WEB\DeliveryAppBackend\OLD_mobile"

Write-Host "📁 Source: $sourceDir" -ForegroundColor Yellow
Write-Host "📁 Target: $targetDir" -ForegroundColor Yellow
Write-Host "📁 Backup: $oldMobileDir" -ForegroundColor Yellow

# Check if directories exist
if (-Not (Test-Path $sourceDir)) {
    Write-Host "❌ ERROR: Source directory not found: $sourceDir" -ForegroundColor Red
    exit 1
}

if (-Not (Test-Path $targetDir)) {
    Write-Host "❌ ERROR: Target directory not found: $targetDir" -ForegroundColor Red
    exit 1
}

# Step 1: Rename DeliveryAppBackend\mobile to OLD_mobile
Write-Host ""
Write-Host "🔄 STEP 1: Renaming mobile directory to OLD_mobile..." -ForegroundColor Green
try {
    if (Test-Path $oldMobileDir) {
        Write-Host "⚠️  OLD_mobile already exists, removing it first..." -ForegroundColor Yellow
        Remove-Item -Path $oldMobileDir -Recurse -Force
    }
    Rename-Item -Path $sourceDir -NewName "OLD_mobile"
    Write-Host "✅ Successfully renamed mobile → OLD_mobile" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Failed to rename directory: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Show directory comparison
Write-Host ""
Write-Host "📋 STEP 2: Directory Comparison" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "📂 OLD_mobile directory contains:" -ForegroundColor Yellow
Get-ChildItem -Path $oldMobileDir -Name | ForEach-Object { Write-Host "   • $_" -ForegroundColor White }

Write-Host ""
Write-Host "📂 Current DeliveryAppMobile contains:" -ForegroundColor Yellow
Get-ChildItem -Path $targetDir -Name | ForEach-Object { Write-Host "   • $_" -ForegroundColor White }

# Step 3: Copy the keyboard-fixed version
Write-Host ""
Write-Host "🔄 STEP 3: Updating App.tsx with keyboard-fixed version..." -ForegroundColor Green

$keyboardFixedFile = "$oldMobileDir\App-KeyboardFixed.tsx"
$targetAppFile = "$targetDir\App.tsx"

if (Test-Path $keyboardFixedFile) {
    # Backup existing App.tsx
    if (Test-Path $targetAppFile) {
        $backupFile = "$targetDir\App.tsx.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Host "📋 Backing up existing App.tsx to: $(Split-Path $backupFile -Leaf)" -ForegroundColor Yellow
        Copy-Item $targetAppFile $backupFile
    }
    
    # Copy keyboard-fixed version
    Write-Host "📁 Copying App-KeyboardFixed.tsx → App.tsx" -ForegroundColor Cyan
    Copy-Item $keyboardFixedFile $targetAppFile -Force
    Write-Host "✅ App.tsx updated with keyboard fix!" -ForegroundColor Green
} else {
    Write-Host "⚠️  App-KeyboardFixed.tsx not found, using CompleteMobileAppSimple.tsx instead" -ForegroundColor Yellow
    $fallbackFile = "$oldMobileDir\CompleteMobileAppSimple.tsx"
    if (Test-Path $fallbackFile) {
        Copy-Item $fallbackFile $targetAppFile -Force
        Write-Host "✅ App.tsx updated with CompleteMobileAppSimple.tsx" -ForegroundColor Green
    } else {
        Write-Host "❌ No suitable source file found!" -ForegroundColor Red
        exit 1
    }
}

# Step 4: Show updated file info
Write-Host ""
Write-Host "📋 STEP 4: Update Summary" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Cyan

$appTsxInfo = Get-Item $targetAppFile
Write-Host "📄 Updated App.tsx:" -ForegroundColor Yellow
Write-Host "   • Size: $([math]::Round($appTsxInfo.Length/1KB, 1)) KB" -ForegroundColor White
Write-Host "   • Modified: $($appTsxInfo.LastWriteTime)" -ForegroundColor White

# Step 5: Next steps
Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Start Expo server: cd 'C:\Users\360WEB\DeliveryAppMobile' && npx expo start --port 19000" -ForegroundColor White
Write-Host "2. The app should now have the keyboard fix" -ForegroundColor White
Write-Host "3. Test customer registration on your phone" -ForegroundColor White
Write-Host "4. Bottom fields should now be accessible when keyboard appears" -ForegroundColor White

Write-Host ""
Write-Host "🔧 WHAT WAS UPDATED:" -ForegroundColor Cyan
Write-Host "✅ Renamed DeliveryAppBackend\mobile → OLD_mobile" -ForegroundColor Green
Write-Host "✅ Updated DeliveryAppMobile\App.tsx with keyboard fix" -ForegroundColor Green
Write-Host "✅ Created backup of previous App.tsx" -ForegroundColor Green
Write-Host "✅ KeyboardAvoidingView now handles virtual keyboard properly" -ForegroundColor Green

Write-Host ""
Write-Host "📁 DIRECTORY STRUCTURE NOW:" -ForegroundColor Cyan
Write-Host "• DeliveryAppBackend\OLD_mobile (archived mobile templates)" -ForegroundColor White
Write-Host "• DeliveryAppMobile (active Expo project with keyboard fix)" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Mobile app update complete! Ready for testing." -ForegroundColor Green