# gets deliveries using your last token
# test-api.ps1
# Run with: .\test-api.ps1

# --- CONFIG ---
$ApiUrl = "http://127.0.0.1:8000/api/deliveries/"
$TokenFile = ".\last-token.txt"

# --- READ TOKEN ---
if (-Not (Test-Path $TokenFile)) {
    Write-Host "No token found. Run get-token.ps1 first!" -ForegroundColor Red
    exit 1
}

$AccessToken = Get-Content $TokenFile | Select-Object -First 1

# --- CALL API ---
$response = Invoke-RestMethod -Uri $ApiUrl -Headers @{Authorization = "Bearer $AccessToken"} -Method Get

# --- PRINT RESULT ---
Write-Host "`nDeliveries API Response:" -ForegroundColor Cyan
$response | ConvertTo-Json -Depth 10
