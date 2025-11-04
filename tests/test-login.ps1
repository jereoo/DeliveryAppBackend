# Test Login Script for DeliveryApp Backend

Write-Host "🧪 Testing API Authentication..." -ForegroundColor Yellow

$body = @{
  username = "admin"
  password = "w3r3w0lf"
} | ConvertTo-Json

try {
  $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Headers @{"Content-Type" = "application/json" } -Body $body
    
  Write-Host "✅ Login Success!" -ForegroundColor Green
  Write-Host "Response:" -ForegroundColor Cyan
  $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
    
  # Save token for testing
  $token = ($response.Content | ConvertFrom-Json).access
  $token | Out-File -FilePath "last-token.txt" -Encoding UTF8
  Write-Host "✅ Token saved to last-token.txt" -ForegroundColor Green
    
}
catch {
  Write-Host "❌ Login Failed!" -ForegroundColor Red
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}