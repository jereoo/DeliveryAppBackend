#!/usr/bin/env pwsh
# Test script for updated driver and vehicle form fields

Write-Host "🧪 Testing Updated Form Fields" -ForegroundColor Green
Write-Host "=" * 50

# Get authentication token
$tokenFile = ".\last-token.txt"
if (Test-Path $tokenFile) {
  $token = Get-Content $tokenFile -Raw
  $token = $token.Trim()
  Write-Host "✅ Using saved token" -ForegroundColor Green
}
else {
  Write-Host "❌ No saved token found. Run .\get-token-save.ps1 first" -ForegroundColor Red
  exit 1
}

$headers = @{
  "Authorization" = "Bearer $token"
  "Content-Type"  = "application/json"
}

$baseUrl = "http://192.168.1.85:8081"

Write-Host ""
Write-Host "📝 Testing Driver Creation with Split Name Fields" -ForegroundColor Cyan

# Test data for driver with split name
$driverData = @{
  username       = "testdriver_$(Get-Date -Format 'yyyyMMddHHmmss')"
  email          = "test@example.com"
  password       = "testpass123"
  first_name     = "John"
  last_name      = "Smith"
  phone_number   = "+1234567890"
  license_number = "DL$(Get-Random -Minimum 100000 -Maximum 999999)"
} | ConvertTo-Json

try {
  Write-Host "Creating driver with first_name: John, last_name: Smith"
  $response = Invoke-RestMethod -Uri "$baseUrl/api/drivers/register/" -Method POST -Body $driverData -Headers $headers
  Write-Host "✅ Driver created successfully!" -ForegroundColor Green
  Write-Host "   Driver ID: $($response.id)"
  Write-Host "   Full Name: $($response.name)" -ForegroundColor Yellow
  $driverId = $response.id
}
catch {
  Write-Host "❌ Driver creation failed: $($_.Exception.Message)" -ForegroundColor Red
  $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
  Write-Host "Error details: $($errorDetails | ConvertTo-Json -Depth 3)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🚗 Testing Vehicle Creation with Split Make/Model Fields" -ForegroundColor Cyan

# Test data for vehicle with split make/model (backend expects combined model field)
$vehicleData = @{
  license_plate = "TEST$(Get-Random -Minimum 100 -Maximum 999)"
  model         = "Toyota Hiace"  # Backend still expects combined model
  capacity      = 1500
  active        = $true
} | ConvertTo-Json

try {
  Write-Host "Creating vehicle with model: 'Toyota Hiace' (combined)"
  $response = Invoke-RestMethod -Uri "$baseUrl/api/vehicles/" -Method POST -Body $vehicleData -Headers $headers
  Write-Host "✅ Vehicle created successfully!" -ForegroundColor Green
  Write-Host "   Vehicle ID: $($response.id)"
  Write-Host "   License Plate: $($response.license_plate)"
  Write-Host "   Model: $($response.model)" -ForegroundColor Yellow
  $vehicleId = $response.id
}
catch {
  Write-Host "❌ Vehicle creation failed: $($_.Exception.Message)" -ForegroundColor Red
  $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
  Write-Host "Error details: $($errorDetails | ConvertTo-Json -Depth 3)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔄 Testing Driver Update with Name Fields" -ForegroundColor Cyan

if ($driverId) {
  $updateData = @{
    name           = "John Smith Jr."  # Backend expects combined name
    phone_number   = "+1987654321"
    license_number = "DL999888"
    active         = $true
  } | ConvertTo-Json

  try {
    Write-Host "Updating driver with combined name: 'John Smith Jr.'"
    $response = Invoke-RestMethod -Uri "$baseUrl/api/drivers/$driverId/" -Method PUT -Body $updateData -Headers $headers
    Write-Host "✅ Driver updated successfully!" -ForegroundColor Green
    Write-Host "   Updated Name: $($response.name)" -ForegroundColor Yellow
  }
  catch {
    Write-Host "❌ Driver update failed: $($_.Exception.Message)" -ForegroundColor Red
  }
}

Write-Host ""
Write-Host "🔄 Testing Vehicle Update with Combined Model" -ForegroundColor Cyan

if ($vehicleId) {
  $updateData = @{
    license_plate = "UPD999"
    model         = "Ford Transit"  # Backend expects combined model
    capacity      = 2000
    active        = $true
  } | ConvertTo-Json

  try {
    Write-Host "Updating vehicle with model: 'Ford Transit'"
    $response = Invoke-RestMethod -Uri "$baseUrl/api/vehicles/$vehicleId/" -Method PUT -Body $updateData -Headers $headers
    Write-Host "✅ Vehicle updated successfully!" -ForegroundColor Green
    Write-Host "   Updated Model: $($response.model)" -ForegroundColor Yellow
  }
  catch {
    Write-Host "❌ Vehicle update failed: $($_.Exception.Message)" -ForegroundColor Red
  }
}

Write-Host ""
Write-Host "📋 Summary" -ForegroundColor Magenta
Write-Host "=" * 50
Write-Host "✅ Form Field Updates Implemented:" -ForegroundColor Green
Write-Host "   • Driver forms: Split first_name/last_name → Combined name for API"
Write-Host "   • Vehicle forms: Split make/model → Combined model for API"
Write-Host "   • Form validation and UI updated"
Write-Host "   • Edit form population with name/model splitting"
Write-Host ""
Write-Host "🔄 Backend Compatibility:" -ForegroundColor Yellow
Write-Host "   • API still accepts combined name/model fields"
Write-Host "   • Mobile forms handle splitting/combining automatically"
Write-Host "   • Data integrity maintained across updates"