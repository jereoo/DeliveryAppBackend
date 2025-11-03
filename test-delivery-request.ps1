# Test delivery request with exact mobile app data
Write-Host "Testing delivery request endpoint..." -ForegroundColor Green

# Read token
if (Test-Path 'last-token.txt') {
    $token = Get-Content 'last-token.txt' -Raw
    $token = $token.Trim()
    
    Write-Host "Using token: $($token.Substring(0,20))..." -ForegroundColor Yellow
    
    # Test data exactly as sent by mobile app
    $headers = @{
        'Content-Type'  = 'application/json'
        'Authorization' = "Bearer $token"
    }
    
    $body = @{
        'dropoff_location'        = 'Brent'
        'item_description'        = 'Chili dog'
        'pickup_location'         = ''
        'same_pickup_as_customer' = $true
        'use_preferred_pickup'    = $false
    } | ConvertTo-Json
    
    Write-Host "Request body: $body" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri 'http://192.168.1.77:8081/api/deliveries/request_delivery/' -Method POST -Headers $headers -Body $body
        Write-Host "SUCCESS!" -ForegroundColor Green
        Write-Host "Response:" -ForegroundColor Yellow
        $response | ConvertTo-Json -Depth 3
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails) {
            Write-Host "Error Details:" -ForegroundColor Yellow
            Write-Host $_.ErrorDetails.Message -ForegroundColor Yellow
        }
    }
}
else {
    Write-Host "No token found in last-token.txt" -ForegroundColor Red
    Write-Host "Run .\get-token-save.ps1 first" -ForegroundColor Yellow
}