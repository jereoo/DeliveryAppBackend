# 📱 START MANUAL TESTING - Quick Launch Script
# Starts both backend and mobile app for manual device testing

Write-Host "🚀 STARTING MANUAL TESTING ENVIRONMENT" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Check if we're in the right directory
$currentDir = Get-Location
if ($currentDir.Path -notlike "*DeliveryAppBackend*") {
    Write-Host "⚠️  Please run this script from DeliveryAppBackend directory" -ForegroundColor Yellow
    Write-Host "Current directory: $currentDir" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📍 Current directory: $currentDir" -ForegroundColor Green

# Verify mobile app exists
$mobileAppPath = "C:\Users\360WEB\DeliveryAppMobile"
if (-not (Test-Path $mobileAppPath)) {
    Write-Host "❌ Mobile app directory not found: $mobileAppPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📱 Mobile app found: $mobileAppPath" -ForegroundColor Green

# Step 1: Start Backend Server
Write-Host "`n🔧 STEP 1: Starting Backend Server..." -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Gray

try {
    # Start backend in background
    Write-Host "Starting Django backend server..." -ForegroundColor White
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$currentDir'; .\start-backend-simple.ps1" -WindowStyle Normal
    
    # Give backend time to start
    Write-Host "⏳ Waiting for backend to initialize (10 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Test backend connectivity
    try {
        $response = Invoke-RestMethod -Uri "http://192.168.1.85:8081/api/customers/register/" -Method OPTIONS -TimeoutSec 5
        Write-Host "✅ Backend server is running and accessible!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Backend may still be starting up. Check the backend window for status." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error starting backend: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Start Mobile App
Write-Host "`n📱 STEP 2: Starting Mobile App..." -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Gray

try {
    Write-Host "Starting Expo development server..." -ForegroundColor White
    Write-Host "📋 This will open a new terminal window with QR code for scanning" -ForegroundColor Cyan
    
    # Start mobile app in new terminal
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd '$mobileAppPath'; Write-Host '📱 MOBILE APP STARTING...' -ForegroundColor Green; Write-Host 'Scan the QR code with your phone camera or Expo Go app' -ForegroundColor Yellow; npx expo start --port 19000" -WindowStyle Normal
    
    Write-Host "✅ Mobile app terminal opened!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error starting mobile app: $_" -ForegroundColor Red
    Write-Host "💡 You can start it manually: cd $mobileAppPath && npx expo start" -ForegroundColor Yellow
}

# Step 3: Display Instructions
Write-Host "`n📋 MANUAL TESTING INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

Write-Host "`n🔧 SERVERS STATUS:" -ForegroundColor Yellow
Write-Host "✅ Backend Server: http://192.168.1.85:8081 (check backend terminal)" -ForegroundColor Green
Write-Host "✅ Mobile App: Expo server starting (check mobile terminal for QR code)" -ForegroundColor Green

Write-Host "`n📱 ON YOUR MOBILE DEVICE:" -ForegroundColor Yellow
Write-Host "1. Install 'Expo Go' app from App Store (iOS) or Google Play (Android)" -ForegroundColor White
Write-Host "2. Make sure your phone is on the same Wi-Fi network as this computer" -ForegroundColor White
Write-Host "3. Open Expo Go app and scan the QR code from the mobile terminal" -ForegroundColor White
Write-Host "4. App should load automatically" -ForegroundColor White

Write-Host "`n🧪 TESTING CHECKLIST:" -ForegroundColor Yellow
Write-Host "1. ✅ App loads without crashes" -ForegroundColor White
Write-Host "2. ✅ Network connection works (shows connected status)" -ForegroundColor White
Write-Host "3. ✅ Customer registration works" -ForegroundColor White
Write-Host "4. ✅ Login with new account works" -ForegroundColor White
Write-Host "5. ✅ View customer profile works" -ForegroundColor White
Write-Host "6. ✅ Edit customer profile works" -ForegroundColor White
Write-Host "7. ✅ Delete customer account works" -ForegroundColor White

Write-Host "`n📖 DETAILED TESTING GUIDE:" -ForegroundColor Yellow
Write-Host "📄 See: MOBILE_CRUD_MANUAL_TESTING_GUIDE.md for complete testing instructions" -ForegroundColor Cyan

Write-Host "`n🚨 TROUBLESHOOTING:" -ForegroundColor Yellow
Write-Host "- If app won't connect: Check both devices on same Wi-Fi" -ForegroundColor White
Write-Host "- If QR won't scan: Try better lighting or type URL manually in Expo Go" -ForegroundColor White
Write-Host "- If app crashes: Shake device → 'Reload' to restart" -ForegroundColor White
Write-Host "- If registration fails: Try different username (must be unique)" -ForegroundColor White

Write-Host "`n✅ WHEN TESTING COMPLETE:" -ForegroundColor Yellow
Write-Host "- Close both terminal windows (backend and mobile)" -ForegroundColor White
Write-Host "- Report results: Working features and any issues found" -ForegroundColor White
Write-Host "- Next step: Implement Driver CRUD screens" -ForegroundColor White

Write-Host "`n🎯 SUCCESS CRITERIA:" -ForegroundColor Green
Write-Host "All 7 test items above should work without crashes or errors" -ForegroundColor White

Write-Host "`n🚀 READY FOR MANUAL TESTING!" -ForegroundColor Green
Write-Host "Check the terminal windows for backend/mobile status and QR code" -ForegroundColor Yellow

Read-Host "`nPress Enter to close this window (servers will continue running)"