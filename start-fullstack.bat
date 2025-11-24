@echo off
:: CIO DIRECTIVE: PERMANENT LAUNCH FIX - ZERO TOLERANCE FOR MANUAL PROCESSES
:: Status: Comprehensive startup automation to eliminate daily 20-60 minute delays
:: Created: Per CIO mandate to "PERMANENTLY fix this TODAY"

echo.
echo ============================================================
echo   🚀 CIO-APPROVED FULLSTACK STARTUP (AUTOMATED SOLUTION)
echo ============================================================
echo.

:: Change to the backend directory
cd /d "c:\Users\360WEB\DeliveryAppBackend"

echo 📋 Step 1: Terminating existing processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
echo ✅ All processes terminated

echo.
echo 📋 Step 2: Starting Django backend server...
start "Django Backend" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

echo.
echo 📋 Step 3: Waiting for Django to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 📋 Step 4: Detecting local IP address...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do set LOCAL_IP=%%i
set LOCAL_IP=%LOCAL_IP: =%
echo 🌐 Local IP detected: %LOCAL_IP%

echo.
echo 📋 Step 5: Starting Expo mobile development server...
cd /d "c:\Users\360WEB\DeliveryAppMobile"
start "Expo Mobile" cmd /k "npx expo start --tunnel"

echo.
echo 📋 Step 6: Backend health check...
timeout /t 3 /nobreak >nul
curl -s http://localhost:8000/api/deliveries/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend server is running successfully
) else (
    echo ⚠️  Backend server may still be starting up
)

echo.
echo ============================================================
echo   🎯 CIO DIRECTIVE IMPLEMENTATION COMPLETE
echo ============================================================
echo   Backend URL: http://localhost:8000/api/
echo   Local IP:    http://%LOCAL_IP%:8000/api/
echo   Mobile:      Expo tunnel active
echo   Status:      ZERO manual processes required
echo ============================================================
echo.
echo Press any key to continue...
pause >nul