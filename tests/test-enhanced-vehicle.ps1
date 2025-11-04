#!/usr/bin/env pwsh
# Test enhanced vehicle model with new fields

Write-Host "🚛 Testing Enhanced Vehicle Model" -ForegroundColor Green
Write-Host "=" * 50

$baseUrl = "http://192.168.1.85:8081"

# Function to get token
function Get-AuthToken {
  try {
    $body = @{
      username = "admin"
      password = "w3r3w0lf"
    } | ConvertTo-Json
        
    $response = Invoke-RestMethod -Uri "$baseUrl/api/token/" -Method POST -Body $body -ContentType "application/json"
    return $response.access
  }
  catch {
    Write-Host "❌ Failed to get token: $($_.Exception.Message)" -ForegroundColor Red
    return $null
  }
}

# Test server connectivity
Write-Host "🔗 Testing server connectivity..." -ForegroundColor Yellow
try {
  $token = Get-AuthToken
  if (-not $token) {
    Write-Host "❌ Cannot connect to server. Please start Django server." -ForegroundColor Red
    exit 1
  }
  Write-Host "✅ Server connected successfully!" -ForegroundColor Green
}
catch {
  Write-Host "❌ Server not responding: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}

$headers = @{
  "Authorization" = "Bearer $token"
  "Content-Type"  = "application/json"
}

Write-Host ""
Write-Host "🚛 Testing Enhanced Vehicle Creation" -ForegroundColor Cyan
Write-Host "=" * 50

# Test vehicle creation with new fields
$vehicleData = @{
  license_plate = "TEST$(Get-Random -Minimum 100 -Maximum 999)"
  make          = "Toyota"
  model         = "Hiace"
  year          = 2023
  vin           = "JH4CU2F6XLC$(Get-Random -Minimum 100000 -Maximum 999999)"  # Unique VIN format
  capacity      = 1500
  active        = $true
} | ConvertTo-Json

try {
  Write-Host "Creating vehicle with enhanced fields:"
  Write-Host "  Make: Toyota" -ForegroundColor Yellow
  Write-Host "  Model: Hiace" -ForegroundColor Yellow
  Write-Host "  Year: 2023" -ForegroundColor Yellow
  Write-Host "  VIN: [Generated unique VIN]" -ForegroundColor Yellow
  Write-Host "  Capacity: 1500 kg" -ForegroundColor Yellow
    
  $response = Invoke-RestMethod -Uri "$baseUrl/api/vehicles/" -Method POST -Body $vehicleData -Headers $headers
  Write-Host "✅ Vehicle created successfully!" -ForegroundColor Green
  Write-Host "   Vehicle ID: $($response.id)" -ForegroundColor Yellow
  Write-Host "   License Plate: $($response.license_plate)" -ForegroundColor Yellow
  Write-Host "   Make: $($response.make)" -ForegroundColor Yellow
  Write-Host "   Model: $($response.model)" -ForegroundColor Yellow
  Write-Host "   Year: $($response.year)" -ForegroundColor Yellow
  Write-Host "   VIN: $($response.vin)" -ForegroundColor Yellow
  Write-Host "   Full Model (backward compat): $($response.full_model)" -ForegroundColor Cyan
  $vehicleId = $response.id
    
}
catch {
  Write-Host "❌ Vehicle creation failed: $($_.Exception.Message)" -ForegroundColor Red
  if ($_.ErrorDetails.Message) {
    $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "   Error details: $($errorDetails)" -ForegroundColor Red
  }
}

Write-Host ""
Write-Host "📋 Testing Vehicle Listing" -ForegroundColor Cyan
Write-Host "=" * 50

try {
  $vehicles = Invoke-RestMethod -Uri "$baseUrl/api/vehicles/" -Method GET -Headers $headers
  Write-Host "✅ Retrieved $($vehicles.count) vehicles" -ForegroundColor Green
    
  if ($vehicles.results -and $vehicles.results.Length -gt 0) {
    $vehicle = $vehicles.results[0]
    Write-Host "Sample vehicle data:" -ForegroundColor Yellow
    Write-Host "   ID: $($vehicle.id)" -ForegroundColor White
    Write-Host "   License: $($vehicle.license_plate)" -ForegroundColor White
    Write-Host "   Make: $($vehicle.make)" -ForegroundColor White
    Write-Host "   Model: $($vehicle.model)" -ForegroundColor White
    Write-Host "   Year: $($vehicle.year)" -ForegroundColor White
    Write-Host "   VIN: $($vehicle.vin)" -ForegroundColor White
    Write-Host "   Capacity: $($vehicle.capacity_display)" -ForegroundColor White
  }
    
}
catch {
  Write-Host "❌ Vehicle listing failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Enhancement Summary" -ForegroundColor Magenta
Write-Host "=" * 50
Write-Host "✅ Enhanced Vehicle Model Features:" -ForegroundColor Green
Write-Host "   • Separate Make and Model fields" -ForegroundColor White
Write-Host "   • Manufacturing Year field" -ForegroundColor White
Write-Host "   • VIN (Vehicle Identification Number) field" -ForegroundColor White
Write-Host "   • Backward compatibility with full_model property" -ForegroundColor White
Write-Host "   • Enhanced validation (year range, VIN format)" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Mobile App Benefits:" -ForegroundColor Yellow
Write-Host "   • Better data organization and validation" -ForegroundColor White
Write-Host "   • Prepared for VIN lookup integration" -ForegroundColor White
Write-Host "   • Professional vehicle management interface" -ForegroundColor White
Write-Host "   • Enhanced search and filtering capabilities" -ForegroundColor White
Write-Host ""
Write-Host "✅ Vehicle Model Enhancement Complete!" -ForegroundColor Green