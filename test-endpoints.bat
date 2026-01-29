@echo off
echo Testing DeliveryApp Backend Endpoints via Ngrok
echo =================================================

set BASE_URL=https://shakita-unlopped-colten.ngrok-free.dev/api

echo Testing /api/deliveries/ ...
curl -k -s -o nul -w "Status: %%{http_code}\n" %BASE_URL%/deliveries/

echo.
echo Testing /api/drivers/ ...
curl -k -s -o nul -w "Status: %%{http_code}\n" %BASE_URL%/drivers/

echo.
echo Testing /api/vehicles/ ...
curl -k -s -o nul -w "Status: %%{http_code}\n" %BASE_URL%/vehicles/

echo.
echo Testing /api/token/ (POST with dummy data) ...
curl -k -s -o nul -w "Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"test\"}" %BASE_URL%/token/

echo.
echo Testing /api/customers/register/ (POST) ...
curl -k -s -o nul -w "Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"test\",\"email\":\"test@test.com\"}" %BASE_URL%/customers/register/

echo.
echo =================================================
echo Expected: 401 for GET endpoints (unauthenticated)
echo Expected: 400/401 for POST endpoints
echo If all show 404, ngrok tunnel is not forwarding correctly.
echo If 401, backend is working - app should connect.
echo =================================================
pause