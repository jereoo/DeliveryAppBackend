# Test all API endpoints with admin credentials
Write-Host "=== DELIVERY APP API ENDPOINT TESTING ===" -ForegroundColor Green
Write-Host ""

$baseUrl = "http://127.0.0.1:8081"
$headers = @{ 'Content-Type' = 'application/json' }

# Step 1: Get Authentication Token
Write-Host "1. AUTHENTICATION TEST" -ForegroundColor Cyan
$authData = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    $tokenResponse = Invoke-RestMethod -Uri "$baseUrl/api/token/" -Method POST -Body $authData -Headers $headers
    Write-Host "✅ Authentication successful!" -ForegroundColor Green
    Write-Host "   Access Token: $($tokenResponse.access.Substring(0,30))..." -ForegroundColor Gray
    
    # Save token for other scripts
    $tokenResponse.access | Out-File "last-token.txt" -NoNewline
    
    # Set up authenticated headers
    $authHeaders = @{
        'Content-Type'  = 'application/json'
        'Authorization' = "Bearer $($tokenResponse.access)"
    }
}
catch {
    Write-Host "❌ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Test API Root
Write-Host "2. API ROOT TEST" -ForegroundColor Cyan
try {
    $apiRoot = Invoke-RestMethod -Uri "$baseUrl/api/" -Method GET -Headers $authHeaders
    Write-Host "✅ API root accessible" -ForegroundColor Green
    Write-Host "   Available endpoints: $($apiRoot.PSObject.Properties.Name -join ', ')" -ForegroundColor Gray
}
catch {
    Write-Host "❌ API root failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Step 3: Test Deliveries Endpoint
Write-Host "3. DELIVERIES ENDPOINT TEST" -ForegroundColor Cyan
try {
    $deliveries = Invoke-RestMethod -Uri "$baseUrl/api/deliveries/" -Method GET -Headers $authHeaders
    Write-Host "✅ Deliveries endpoint accessible" -ForegroundColor Green
    Write-Host "   Total deliveries: $($deliveries.count)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Deliveries endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Test Customers Endpoint
Write-Host "4. CUSTOMERS ENDPOINT TEST" -ForegroundColor Cyan
try {
    $customers = Invoke-RestMethod -Uri "$baseUrl/api/customers/" -Method GET -Headers $authHeaders
    Write-Host "✅ Customers endpoint accessible" -ForegroundColor Green
    Write-Host "   Total customers: $($customers.count)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Customers endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Test Drivers Endpoint
Write-Host "5. DRIVERS ENDPOINT TEST" -ForegroundColor Cyan
try {
    $drivers = Invoke-RestMethod -Uri "$baseUrl/api/drivers/" -Method GET -Headers $authHeaders
    Write-Host "✅ Drivers endpoint accessible" -ForegroundColor Green
    Write-Host "   Total drivers: $($drivers.count)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Drivers endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Test Vehicles Endpoint
Write-Host "6. VEHICLES ENDPOINT TEST" -ForegroundColor Cyan
try {
    $vehicles = Invoke-RestMethod -Uri "$baseUrl/api/vehicles/" -Method GET -Headers $authHeaders
    Write-Host "✅ Vehicles endpoint accessible" -ForegroundColor Green
    Write-Host "   Total vehicles: $($vehicles.count)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Vehicles endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Test Driver-Vehicle Assignments
Write-Host "7. DRIVER-VEHICLE ASSIGNMENTS TEST" -ForegroundColor Cyan
try {
    $assignments = Invoke-RestMethod -Uri "$baseUrl/api/driver-vehicles/" -Method GET -Headers $authHeaders
    Write-Host "✅ Driver-Vehicle assignments endpoint accessible" -ForegroundColor Green
    Write-Host "   Total assignments: $($assignments.count)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Driver-Vehicle assignments failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Test Delivery Assignments
Write-Host "8. DELIVERY ASSIGNMENTS TEST" -ForegroundColor Cyan
try {
    $delAssignments = Invoke-RestMethod -Uri "$baseUrl/api/assignments/" -Method GET -Headers $authHeaders
    Write-Host "✅ Delivery assignments endpoint accessible" -ForegroundColor Green
    Write-Host "   Total delivery assignments: $($delAssignments.count)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Delivery assignments failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== API ENDPOINT TESTING COMPLETE ===" -ForegroundColor Green
Write-Host "Token saved to last-token.txt for further testing" -ForegroundColor Yellow
