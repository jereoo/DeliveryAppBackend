# Update Mobile App Network Configuration
# Updates the NETWORK_ENDPOINTS array in DeliveryAppMobile/App.tsx with current IP

param(
    [string]$CurrentIP = "192.168.1.85",
    [string]$MobilePath = "C:\Users\360WEB\DeliveryAppMobile\App.tsx"
)

Write-Host "🔧 Updating Mobile App Network Configuration..." -ForegroundColor Cyan
Write-Host "Current IP: $CurrentIP" -ForegroundColor Yellow
Write-Host "Mobile App: $MobilePath" -ForegroundColor Yellow

# Check if mobile app exists
if (-not (Test-Path $MobilePath)) {
    Write-Host "❌ Mobile app not found at: $MobilePath" -ForegroundColor Red
    Write-Host "Available directories:" -ForegroundColor Yellow
    Get-ChildItem "C:\Users\360WEB" -Directory | Where-Object {$_.Name -like "*Delivery*"} | ForEach-Object {
        Write-Host "  - $($_.FullName)" -ForegroundColor Gray
    }
    exit 1
}

# Read current App.tsx content
$content = Get-Content $MobilePath -Raw

Write-Host "`n📋 Current NETWORK_ENDPOINTS configuration:" -ForegroundColor Yellow
$content | Select-String -Pattern "NETWORK_ENDPOINTS[\s\S]*?];" | ForEach-Object {
    $_.Matches[0].Value -split "`n" | ForEach-Object {
        if ($_ -match "url:|name:") {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
}

# Define the new NETWORK_ENDPOINTS array
$newNetworkEndpoints = @"
    const NETWORK_ENDPOINTS = [
      { url: 'http://$CurrentIP:8081', name: 'Current Network (Auto-detected)' },
      { url: 'http://192.168.1.87:8081', name: 'Home Office Network' },
      { url: 'http://192.168.1.82:8081', name: 'Home Office Network (Alt)' },
      { url: 'http://172.20.10.6:8081', name: 'Mobile Hotspot' }
    ];
"@

# Replace the NETWORK_ENDPOINTS array
$pattern = "const NETWORK_ENDPOINTS = \[[\s\S]*?\];"
$newContent = $content -replace $pattern, $newNetworkEndpoints

if ($newContent -ne $content) {
    # Create backup
    $backupPath = $MobilePath + ".backup." + (Get-Date -Format "yyyyMMdd_HHmmss")
    Copy-Item $MobilePath $backupPath
    Write-Host "✅ Backup created: $backupPath" -ForegroundColor Green
    
    # Write updated content
    Set-Content $MobilePath $newContent -Encoding UTF8
    Write-Host "✅ Mobile app network configuration updated!" -ForegroundColor Green
    
    Write-Host "`n📋 New NETWORK_ENDPOINTS configuration:" -ForegroundColor Yellow
    $newContent | Select-String -Pattern "NETWORK_ENDPOINTS[\s\S]*?];" | ForEach-Object {
        $_.Matches[0].Value -split "`n" | ForEach-Object {
            if ($_ -match "url:|name:") {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host "`n🔍 Verification:" -ForegroundColor Cyan
    if ($newContent -match "http://$CurrentIP:8081") {
        Write-Host "✅ Current IP ($CurrentIP) found in configuration" -ForegroundColor Green
    } else {
        Write-Host "❌ Current IP ($CurrentIP) NOT found in configuration" -ForegroundColor Red
    }
    
    Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start mobile app: cd C:\Users\360WEB\DeliveryAppMobile && npx expo start" -ForegroundColor Yellow
    Write-Host "2. The app will now use $CurrentIP:8081 as the primary backend" -ForegroundColor Yellow
    Write-Host "3. Test CRUD operations with the updated network configuration" -ForegroundColor Yellow
    
} else {
    Write-Host "⚠️  No changes needed - configuration already correct" -ForegroundColor Yellow
}