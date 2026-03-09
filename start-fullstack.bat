@echo off
:: LAN-ONLY STARTUP – No Expo tunnel, no ngrok. Phone and PC must be on same Wi-Fi.
:: MARCH 2026: Tunnel mode removed per user request (QR timeout after 100+ attempts).

echo.
echo ============================================================
echo   LAN-ONLY FULLSTACK STARTUP (No tunnel / No ngrok)
echo ============================================================
echo.

:: Change to the backend directory
cd /d "c:\Users\360WEB\DeliveryAppBackend"

echo Step 1: Terminating existing processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
echo All processes terminated

echo.
echo Step 2: Starting Django backend server...
start "Django Backend" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

echo.
echo Step 3: Waiting for Django to initialize...
ping -n 6 127.0.0.1 >nul 2>&1

echo.
echo Step 4: Detecting local IP address (for LAN)...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr /v "127.0.0.1" ^| findstr /v "169.254"') do (
    set "LOCAL_IP=%%i"
    goto :ip_found
)
:ip_found
set LOCAL_IP=%LOCAL_IP: =%
if "%LOCAL_IP%"=="" set LOCAL_IP=192.168.1.80
echo Local IP detected: %LOCAL_IP%

echo.
echo Step 5: Writing LAN backend URL to .env (no tunnel)...
cd /d "c:\Users\360WEB\DeliveryApp"
echo # LAN-only > .env
echo BACKEND_URL=http://%LOCAL_IP%:8000/api >> .env
echo Updated .env with BACKEND_URL=http://%LOCAL_IP%:8000/api

cd /d "c:\Users\360WEB\DeliveryAppMobile"
echo # LAN-only > .env
echo BACKEND_URL=http://%LOCAL_IP%:8000/api >> .env
echo Updated DeliveryAppMobile\.env with BACKEND_URL=http://%LOCAL_IP%:8000/api

echo.
echo Step 6: Starting Expo (LAN only – no tunnel)...
start "Expo Mobile" cmd /k "npx @expo/cli start --clear --port 8081"

echo.
echo Step 7: Backend health check...
ping -n 4 127.0.0.1 >nul 2>&1
curl -s http://localhost:8000/api/health/ >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend server is running
) else (
    echo Backend may still be starting
)

echo.
echo ============================================================
echo   LAN-ONLY STARTUP COMPLETE
echo ============================================================
echo   Backend (LAN):  http://%LOCAL_IP%:8000/api/
echo   Expo (LAN):     Scan QR code – phone must be on same Wi-Fi
echo   No tunnel – no ngrok – no Expo Go tunnel
echo ============================================================
echo.
echo Press any key to continue...
pause >nul
goto :eof

:error
echo.
echo STARTUP FAILED – check messages above
echo.
pause >nul
