# =============================================================================
# UPDATE-MOBILE-NETWORK.PS1 - Mobile App Network Configuration Updater
# =============================================================================
# Updates mobile app network endpoints with current IP address

Write-Host "🔧 Updating Mobile App Network Configuration..." -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan

# Import network detection module
$ModulePath = Join-Path $PSScriptRoot "NetworkDetection.psm1"
if (Test-Path $ModulePath) {
    Import-Module $ModulePath -Force
    Write-Host "✅ Network detection module loaded" -ForegroundColor Green
} else {
    Write-Host "❌ NetworkDetection.psm1 not found. Using fallback IP detection." -ForegroundColor Yellow
}

# Get current IP
try {
    if (Get-Command "Get-LocalIPAddress" -ErrorAction SilentlyContinue) {
        $CurrentIP = Get-LocalIPAddress
    } else {
        # Fallback IP detection
        $CurrentIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*" | Where-Object { $_.IPAddress -like "192.168.*" } | Select-Object -First 1).IPAddress
        if (-not $CurrentIP) {
            $CurrentIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" } | Select-Object -First 1).IPAddress
        }
    }
    
    if (-not $CurrentIP) {
        throw "Could not detect IP address"
    }
    
    Write-Host "🌐 Current IP detected: $CurrentIP" -ForegroundColor Green
} catch {
    Write-Host "❌ Error detecting IP: $_" -ForegroundColor Red
    $CurrentIP = "192.168.1.85"  # fallback to known working IP
    Write-Host "🔄 Using fallback IP: $CurrentIP" -ForegroundColor Yellow
}

# Define mobile app paths
$MobilePaths = @(
    "C:\Users\360WEB\DeliveryAppMobile\App.tsx",
    "C:\Users\360WEB\DeliveryAppBackend\OLD_mobile\COPY_TO_EXPO_APP.tsx",
    "C:\Users\360WEB\DeliveryAppBackend\OLD_mobile\App.tsx",
    "C:\Users\360WEB\DeliveryAppBackend\OLD_mobile\App-KeyboardFixed.tsx",
    "C:\Users\360WEB\DeliveryAppBackend\OLD_mobile\EnhancedMobileApp.tsx",
    "C:\Users\360WEB\DeliveryAppBackend\OLD_mobile\EnhancedMobileAppFixed.tsx"
)

# New NETWORK_ENDPOINTS configuration with current IP first
$NewNetworkConfig = @"
  const NETWORK_ENDPOINTS = [
    { url: 'http://$CurrentIP:8081', name: 'Current Network (Auto-detected)' },
    { url: 'http://192.168.1.87:8081', name: 'Home Office Network' },
    { url: 'http://192.168.1.82:8081', name: 'Home Office Network (Alt)' },
    { url: 'http://172.20.10.6:8081', name: 'Mobile Hotspot' }
  ];
"@

$UpdatedFiles = @()
$SkippedFiles = @()

foreach ($FilePath in $MobilePaths) {
    if (Test-Path $FilePath) {
        try {
            # Read current file content
            $Content = Get-Content $FilePath -Raw
            
            # Check if file contains NETWORK_ENDPOINTS
            if ($Content -match "const NETWORK_ENDPOINTS\s*=") {
                Write-Host "📝 Updating: $FilePath" -ForegroundColor Yellow
                
                # Replace NETWORK_ENDPOINTS section
                $UpdatedContent = $Content -replace "const NETWORK_ENDPOINTS\s*=\s*\[[^\]]*\];", $NewNetworkConfig
                
                # Verify the replacement worked
                if ($UpdatedContent -ne $Content) {
                    # Create backup
                    $BackupPath = "$FilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                    Copy-Item $FilePath $BackupPath
                    
                    # Write updated content
                    Set-Content $FilePath $UpdatedContent -Encoding UTF8
                    
                    Write-Host "✅ Updated: $FilePath" -ForegroundColor Green
                    Write-Host "💾 Backup created: $BackupPath" -ForegroundColor Cyan
                    $UpdatedFiles += $FilePath
                } else {
                    Write-Host "⚠️  No changes needed: $FilePath" -ForegroundColor Yellow
                    $SkippedFiles += $FilePath
                }
            } else {
                Write-Host "⏭️  No NETWORK_ENDPOINTS found: $FilePath" -ForegroundColor Gray
                $SkippedFiles += $FilePath
            }
        } catch {
            Write-Host "❌ Error updating $FilePath`: $_" -ForegroundColor Red
            $SkippedFiles += $FilePath
        }
    } else {
        Write-Host "📂 File not found: $FilePath" -ForegroundColor Gray
        $SkippedFiles += $FilePath
    }
}

# Summary
Write-Host "`n📊 Update Summary:" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "🌐 Current IP: $CurrentIP" -ForegroundColor Green
Write-Host "✅ Updated files: $($UpdatedFiles.Count)" -ForegroundColor Green
Write-Host "⏭️  Skipped files: $($SkippedFiles.Count)" -ForegroundColor Yellow

if ($UpdatedFiles.Count -gt 0) {
    Write-Host "`n✅ Updated Files:" -ForegroundColor Green
    foreach ($file in $UpdatedFiles) {
        Write-Host "   - $file" -ForegroundColor White
    }
}

if ($SkippedFiles.Count -gt 0) {
    Write-Host "`n⏭️  Skipped Files:" -ForegroundColor Yellow
    foreach ($file in $SkippedFiles) {
        Write-Host "   - $file" -ForegroundColor Gray
    }
}

# Display new configuration
Write-Host "`n🔧 New Network Configuration:" -ForegroundColor Cyan
Write-Host $NewNetworkConfig -ForegroundColor White

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host "1. Start mobile app: .\start-mobile.ps1" -ForegroundColor White
Write-Host "2. Test network connectivity in mobile app" -ForegroundColor White
Write-Host "3. Verify CRUD operations work with current IP" -ForegroundColor White

Write-Host "`n📱 Mobile Network Update Complete!" -ForegroundColor Green