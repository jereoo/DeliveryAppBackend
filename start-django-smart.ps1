# Smart Start Script for Django - Network Aware
# This PowerShell script uses the network configuration to start Django appropriately

param(
    [string]$Profile = ""
)

# Function to check if network_config.py exists and is working
function Test-NetworkConfig {
    try {
        $result = python network_config.py status 2>$null
        return $?
    }
    catch {
        return $false
    }
}

# Function to start Django with network configuration
function Start-DjangoWithConfig {
    Write-Host "🌐 Starting Django with network configuration..." -ForegroundColor Green
    
    # Get the appropriate run command from network config
    $runCommand = python -c "from network_config import NetworkConfig; config = NetworkConfig(); print(config.get_django_run_command())"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🚀 Executing: $runCommand" -ForegroundColor Yellow
        Invoke-Expression $runCommand
    } else {
        Write-Host "❌ Failed to get network configuration" -ForegroundColor Red
        Start-DjangoFallback
    }
}

# Function to start Django with fallback settings
function Start-DjangoFallback {
    Write-Host "🔄 Using fallback Django configuration..." -ForegroundColor Yellow
    Write-Host "🚀 Starting Django server on 0.0.0.0:8000 (hotspot mode)" -ForegroundColor Green
    python manage.py runserver 0.0.0.0:8000
}

# Function to change network profile
function Set-NetworkProfile {
    param([string]$NewProfile)
    
    Write-Host "🔧 Changing network profile to: $NewProfile" -ForegroundColor Cyan
    python network_config.py $NewProfile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Network profile updated successfully!" -ForegroundColor Green
        Start-DjangoWithConfig
    } else {
        Write-Host "❌ Failed to update network profile" -ForegroundColor Red
        Start-DjangoFallback
    }
}

# Main script logic
Write-Host "🎯 DeliveryApp Backend - Smart Network Launcher" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Gray

# Activate virtual environment first
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "🐍 Activating virtual environment..." -ForegroundColor Blue
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  Virtual environment not found, proceeding anyway..." -ForegroundColor Yellow
}

# Handle profile parameter
if ($Profile -ne "") {
    if ($Profile -in @("private", "public", "hotspot", "phone")) {
        Set-NetworkProfile -NewProfile $Profile
        exit
    } else {
        Write-Host "❌ Invalid profile. Use: private, public, hotspot, or phone" -ForegroundColor Red
        exit 1
    }
}

# Check if network configuration is available
if (Test-NetworkConfig) {
    Start-DjangoWithConfig
} else {
    Write-Host "⚠️  Network configuration not available, using fallback..." -ForegroundColor Yellow
    Start-DjangoFallback
}