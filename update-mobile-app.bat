@echo off
echo 🚚 DeliveryApp Mobile - Quick App.tsx Update
echo ==========================================

set SOURCE="C:\Users\360WEB\DeliveryAppBackend\mobile\App-KeyboardFixed.tsx"
set TARGET="C:\Users\360WEB\DeliveryAppMobile\App.tsx"

if not exist %SOURCE% (
    echo ❌ ERROR: Source file not found!
    echo Please make sure App-KeyboardFixed.tsx exists.
    pause
    exit /b 1
)

if not exist "C:\Users\360WEB\DeliveryAppMobile" (
    echo ❌ ERROR: DeliveryAppMobile directory not found!
    pause
    exit /b 1
)

echo 📁 Copying keyboard-fixed version...
copy %SOURCE% %TARGET% >nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ SUCCESS: App.tsx updated with keyboard fix!
    echo.
    echo 🎯 NEXT STEPS:
    echo 1. Restart Expo: npx expo start --port 19000
    echo 2. Test customer registration on phone
    echo 3. Bottom fields should now be accessible
    echo.
    echo 🚀 Ready for testing!
) else (
    echo ❌ ERROR: Failed to copy file!
)

pause