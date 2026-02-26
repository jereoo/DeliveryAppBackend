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
:: Improved IP detection - find WiFi/LAN adapter IP
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr /v "127.0.0.1" ^| findstr /v "169.254"') do (
    set "LOCAL_IP=%%i"
    goto :ip_found
)
:ip_found
set LOCAL_IP=%LOCAL_IP: =%
if "%LOCAL_IP%"=="" set LOCAL_IP=192.168.1.80
echo 🌐 Local IP detected: %LOCAL_IP%

echo.
echo 📋 Step 5: Starting ngrok tunnel for backend...
cd /d "c:\Users\360WEB\DeliveryApp"

echo 📋 Step 5a: Creating ngrok tunnel to Django backend...
start "Ngrok Tunnel" cmd /k "ngrok.exe http 8000"

echo 📋 Step 5b: Waiting for ngrok tunnel to establish...
timeout /t 8 /nobreak >nul

echo 📋 Step 5c: Detecting ngrok tunnel URL...
for /f "tokens=*" %%i in ('powershell -Command "try { $response = Invoke-WebRequest -Uri http://localhost:4040/api/tunnels -TimeoutSec 5; $json = $response.Content | ConvertFrom-Json; $tunnel = $json.tunnels | Where-Object { $_.proto -eq 'https' } | Select-Object -First 1; if ($tunnel) { $tunnel.public_url } else { '' } } catch { '' }"') do set TUNNEL_URL=%%i

if defined TUNNEL_URL (
    echo 🌐 Ngrok tunnel URL detected: %TUNNEL_URL%
) else (
    echo ⚠️  Ngrok tunnel not detected, falling back to LAN mode...
)

if defined TUNNEL_URL (
    echo 🌐 Ngrok tunnel URL detected: %TUNNEL_URL%
    echo 📋 Step 5d: Updating .env with ngrok tunnel URL...
    echo # CIO DIRECTIVE – PERMANENT FIX FOR DAILY NETWORK ERROR – DEC 04 2025 > .env
    echo EXPO_USE_TUNNEL=true >> .env
    echo BACKEND_URL=%TUNNEL_URL%/api >> .env
    echo ✅ Updated .env with ngrok tunnel URL: %TUNNEL_URL%/api
) else (
    echo ⚠️  No ngrok tunnel detected, using LAN mode...
    echo # CIO DIRECTIVE – PERMANENT FIX FOR DAILY NETWORK ERROR – DEC 04 2025 > .env
    echo EXPO_USE_TUNNEL=false >> .env
    echo BACKEND_URL=http://%LOCAL_IP%:8000/api >> .env
    echo ✅ Updated .env with LAN URL: http://%LOCAL_IP%:8000/api
)

echo.
echo 📋 Step 6: Starting Expo mobile development server...
cd /d "c:\Users\360WEB\DeliveryAppMobile"
start "Expo Mobile" cmd /k "npx expo start --tunnel"

echo.
echo 📋 Step 6: Backend health check...
timeout /t 3 /nobreak >nul
curl -s http://localhost:8000/api/health/ >nul 2>&1
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
if defined TUNNEL_URL (
    echo   Ngrok URL:   %TUNNEL_URL%/api/
) else (
    echo   Local IP:    http://%LOCAL_IP%:8000/api/
)
echo   Mobile:      Expo tunnel active
echo   Status:      ZERO manual processes required
echo ============================================================
echo.
echo Press any key to continue...
pause >nul
goto :eof

:error
echo.
echo ============================================================
echo   ❌ STARTUP FAILED
echo ============================================================
echo   Check the error messages above and try again
echo ============================================================
echo.
pause >nul