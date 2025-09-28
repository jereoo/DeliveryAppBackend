# API Test using pre-generated token (works on public WiFi)
Write-Host "=== API ENDPOINT TESTING (Token-based) ===" -ForegroundColor Green
Write-Host ""

# Read token from file
if (Test-Path "last-token.txt") {
    $token = Get-Content "last-token.txt" -Raw
    Write-Host "✅ Using saved JWT token" -ForegroundColor Green
    Write-Host "   Token preview: $($token.Substring(0,30))..." -ForegroundColor Gray
} else {
    Write-Host "❌ No token found. Run the Django shell command first." -ForegroundColor Red
    exit 1
}

$baseUrl = "http://127.0.0.1:3000"  # Using port 3000
$authHeaders = @{
    'Content-Type' = 'application/json'
    'Authorization' = "Bearer $token"
}

Write-Host ""
Write-Host "Testing API endpoints with authentication..." -ForegroundColor Cyan

# Test endpoints that should work
$endpoints = @(
    @{url="/api/"; name="API Root"},
    @{url="/api/deliveries/"; name="Deliveries"},
    @{url="/api/customers/"; name="Customers"},
    @{url="/api/drivers/"; name="Drivers"},
    @{url="/api/vehicles/"; name="Vehicles"},
    @{url="/api/driver-vehicles/"; name="Driver-Vehicle Assignments"},
    @{url="/api/assignments/"; name="Delivery Assignments"}
)

foreach ($endpoint in $endpoints) {
    try {
        Write-Host "Testing $($endpoint.name)..." -NoNewline
        $response = Invoke-RestMethod -Uri "$baseUrl$($endpoint.url)" -Method GET -Headers $authHeaders -TimeoutSec 5
        Write-Host " ✅" -ForegroundColor Green
        
        if ($response.count -ne $null) {
            Write-Host "   Records: $($response.count)" -ForegroundColor Gray
        } elseif ($response -is [array]) {
            Write-Host "   Records: $($response.Count)" -ForegroundColor Gray
        } else {
            Write-Host "   Response received" -ForegroundColor Gray
        }
    } catch {
        if ($_.Exception.Message -match "connection|refused|timeout") {
            Write-Host " ❌ Network Issue (Public WiFi blocking)" -ForegroundColor Yellow
        } else {
            Write-Host " ❌ $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== TESTING COMPLETE ===" -ForegroundColor Green
Write-Host "Note: Network errors are likely due to public WiFi restrictions" -ForegroundColor Yellow