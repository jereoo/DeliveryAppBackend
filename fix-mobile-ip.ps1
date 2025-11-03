# Quick Network IP Update for Mobile App
# Updates the mobile app to connect to the correct server IP

Write-Host "🔧 MOBILE APP NETWORK UPDATE" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Get current server IP
$serverIP = "192.168.1.77"
$serverPort = "8081"
$correctEndpoint = "http://$serverIP`:$serverPort"

Write-Host "`n🌐 Server is running on: $correctEndpoint" -ForegroundColor Green

# Check if mobile app directory exists
$mobileDir = "C:\Users\360WEB\DeliveryAppMobile"
if (!(Test-Path $mobileDir)) {
  Write-Host "❌ Mobile app directory not found: $mobileDir" -ForegroundColor Red
  exit 1
}

Set-Location $mobileDir

# Update App.tsx with correct server IP
Write-Host "`n📱 Updating App.tsx network configuration..." -ForegroundColor Yellow

$appFile = "App.tsx"
if (Test-Path $appFile) {
  $content = Get-Content $appFile -Raw
    
  # Replace any 192.168.1.69:8081 with 192.168.1.77:8081
  $updatedContent = $content -replace "192\.168\.1\.69:8081", "$serverIP`:$serverPort"
    
  # Also replace any other common incorrect IPs
  $updatedContent = $updatedContent -replace "192\.168\.1\.79:8081", "$serverIP`:$serverPort"
    
  # Write back to file
  $updatedContent | Set-Content $appFile -Encoding UTF8
    
  Write-Host "✅ App.tsx updated with correct server IP" -ForegroundColor Green
}
else {
  Write-Host "⚠️ App.tsx not found in mobile directory" -ForegroundColor Yellow
}

# Update NetworkConfig files if they exist
$networkConfigs = @(
  "NetworkConfig_Enhanced.js",
  "NetworkConfig_Port8000.js",
  "enhanced_network_config.js"
)

foreach ($configFile in $networkConfigs) {
  if (Test-Path $configFile) {
    Write-Host "`n🔧 Updating $configFile..." -ForegroundColor Yellow
        
    $content = Get-Content $configFile -Raw
        
    # Replace incorrect IPs with correct server IP
    $updatedContent = $content -replace "192\.168\.1\.69:8081", "$serverIP`:$serverPort"
    $updatedContent = $updatedContent -replace "192\.168\.1\.79:8081", "$serverIP`:$serverPort"
    $updatedContent = $updatedContent -replace "192\.168\.1\.77:8000", "$serverIP`:$serverPort"
        
    $updatedContent | Set-Content $configFile -Encoding UTF8
        
    Write-Host "✅ $configFile updated" -ForegroundColor Green
  }
}

Write-Host "`n🎯 MOBILE APP CONFIGURATION UPDATED!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Server URL: $correctEndpoint" -ForegroundColor Gray
Write-Host "Please restart your mobile app (npx expo start)" -ForegroundColor Yellow
Write-Host "Then scan the QR code again" -ForegroundColor Yellow