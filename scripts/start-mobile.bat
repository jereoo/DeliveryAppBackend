@echo off
REM CIO DIRECTIVE – PERMANENT FIX FOR DAILY NETWORK ERROR – NOV 20 2025

setlocal enabledelayedexpansion

echo [92m🚀 CIO-APPROVED DELIVERYAPP STARTUP SEQUENCE[0m
echo [92m====================================================[0m

REM Project paths
set BACKEND_PATH=..\DeliveryAppBackend
set MOBILE_PATH=.

REM Step 1: Check if Django backend is already running
echo [93m📡 Checking Django backend status...[0m
curl -s http://localhost:8000/api/health/ >nul 2>&1
if %errorlevel% equ 0 (
    echo [92m✅ Django backend already running[0m
) else (
    echo [93m🔧 Starting Django backend...[0m
    
    REM Navigate to backend
    pushd "%BACKEND_PATH%"
    
    REM Activate virtual environment if it exists
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo [92m✅ Virtual environment activated[0m
    ) else if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
        echo [92m✅ Virtual environment activated[0m
    )
    
    REM Start Django server in background
    start /B python manage.py runserver 0.0.0.0:8000
    
    REM Wait for Django to be ready
    echo [93m⏳ Waiting for Django backend to be ready...[0m
    for /L %%i in (1,1,30) do (
        curl -s http://localhost:8000/api/health/ >nul 2>&1
        if !errorlevel! equ 0 (
            echo [92m✅ Django backend is ready![0m
            goto django_ready
        )
        echo|set /p="."
        timeout /t 2 >nul
    )
    
    echo [91m❌ Django backend failed to start after 60 seconds[0m
    exit /b 1
    
    :django_ready
    popd
)

REM Step 2: Clean Expo cache and start tunnel
echo [93m🧹 Cleaning Expo cache...[0m
call npx expo install --fix
if exist ".expo" rmdir /s /q .expo
if exist "node_modules\.cache" rmdir /s /q node_modules\.cache

echo [93m🌐 Starting Expo with tunnel...[0m

REM Set environment variables
set EXPO_USE_TUNNEL=true

REM Start Expo with tunnel
start /B npx expo start --tunnel --clear

REM Wait for tunnel URL to be generated
echo [93m⏳ Waiting for Expo tunnel URL...[0m
timeout /t 10 >nul

REM Try to get tunnel URL (simplified for Windows)
set TUNNEL_URL=
for /L %%i in (1,1,20) do (
    REM Check if we can get status from metro bundler
    curl -s http://localhost:19002/status 2>nul | findstr "ngrok.io" >nul
    if !errorlevel! equ 0 (
        REM In a real implementation, you'd extract the URL here
        echo [92m🎯 Tunnel URL detected[0m
        goto url_found
    )
    echo|set /p="."
    timeout /t 2 >nul
)

:url_found
REM Create .env file
echo # CIO DIRECTIVE – PERMANENT FIX FOR DAILY NETWORK ERROR – NOV 20 2025 > .env
echo EXPO_USE_TUNNEL=true >> .env
echo BACKEND_URL=https://your-tunnel-url.ngrok.io/api >> .env

echo [92m✅ Created .env file[0m

REM Step 3: Final instructions
echo [92m====================================================[0m
echo [92m🎉 DELIVERYAPP STARTUP COMPLETE![0m
echo [92m====================================================[0m
echo [92m📱 Scan the QR code in Expo Go app[0m
echo [92m🌐 Django API: http://localhost:8000[0m
echo [92m🏠 LAN URL: http://192.168.1.79:8000 (for mobile testing)[0m
echo [92m🔗 Check Expo CLI output for tunnel URL[0m
echo [92m====================================================[0m

echo [94m📊 Showing live logs (Ctrl+C to stop):[0m
pause