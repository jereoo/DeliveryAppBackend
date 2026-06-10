# Production smoke test - read-only checks + optional auth CRUD when credentials are set.
# Usage:
#   .\scripts\production-smoke-test.ps1
#   $env:ADMIN_USERNAME = "admin"; $env:ADMIN_PASSWORD = "..." ; .\scripts\production-smoke-test.ps1

param(
    [string]$ApiBase = $(if ($env:API_BASE_URL) { $env:API_BASE_URL.TrimEnd('/') } else { 'https://truck-buddy-f14f250ae8b3.herokuapp.com' }),
    [string]$WebUrl = $(if ($env:WEB_URL) { $env:WEB_URL } else { 'https://deliveryapp-mobile.vercel.app' }),
    [string]$AdminUser = $env:ADMIN_USERNAME,
    [string]$AdminPassword = $env:ADMIN_PASSWORD
)

$ErrorActionPreference = 'Stop'
$script:failed = 0
$script:passed = 0
$script:token = $null

function Test-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Host ""
    Write-Host "--- $Name ---" -ForegroundColor Cyan
    try {
        & $Action
        Write-Host "PASS: $Name" -ForegroundColor Green
        $script:passed++
    } catch {
        Write-Host "FAIL: $Name - $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
    }
}

Write-Host "DeliveryApp production smoke test" -ForegroundColor Yellow
Write-Host "API: $ApiBase"
Write-Host "Web: $WebUrl"

Test-Step "API health" {
    $r = Invoke-RestMethod -Uri "$ApiBase/api/health/" -Method GET -TimeoutSec 30
    if ($r.status -ne 'ok') {
        throw "Unexpected health payload"
    }
}

Test-Step "Vercel web root" {
    $resp = Invoke-WebRequest -Uri $WebUrl -UseBasicParsing -TimeoutSec 30
    if ($resp.StatusCode -ne 200) {
        throw "HTTP $($resp.StatusCode)"
    }
}

if (-not $AdminPassword) {
    Write-Host ""
    Write-Host "Skipping authenticated CRUD (set ADMIN_PASSWORD to run full checklist)." -ForegroundColor Yellow
} else {
    $headers = @{ 'Content-Type' = 'application/json' }

    Test-Step "JWT login" {
        $user = if ($AdminUser) { $AdminUser } else { 'admin' }
        $body = @{ username = $user; password = $AdminPassword } | ConvertTo-Json
        $t = Invoke-RestMethod -Uri "$ApiBase/api/token/" -Method POST -Body $body -Headers $headers -TimeoutSec 30
        if (-not $t.access) {
            throw 'No access token in response'
        }
        $script:token = $t.access
    }

    if ($script:token) {
        $authHeaders = @{
            'Content-Type'  = 'application/json'
            'Authorization' = "Bearer $($script:token)"
        }

        Test-Step "List customers (CRUD read)" {
            $null = Invoke-RestMethod -Uri "$ApiBase/api/customers/" -Method GET -Headers $authHeaders -TimeoutSec 30
        }
        Test-Step "List drivers (CRUD read)" {
            $null = Invoke-RestMethod -Uri "$ApiBase/api/drivers/" -Method GET -Headers $authHeaders -TimeoutSec 30
        }
        Test-Step "List vehicles (CRUD read)" {
            $null = Invoke-RestMethod -Uri "$ApiBase/api/vehicles/" -Method GET -Headers $authHeaders -TimeoutSec 30
        }
        Test-Step "List deliveries (CRUD read)" {
            $null = Invoke-RestMethod -Uri "$ApiBase/api/deliveries/" -Method GET -Headers $authHeaders -TimeoutSec 30
        }

        Test-Step "Vehicle lifecycle routes (staff deactivate/reactivate)" {
            # Non-existent id → 404 proves route is registered (not 405 Method Not Allowed on wrong verb)
            try {
                Invoke-RestMethod -Uri "$ApiBase/api/vehicles/999999/deactivate/" -Method POST -Headers $authHeaders -TimeoutSec 30
                throw 'Expected 404 for missing vehicle'
            } catch {
                $status = $null
                if ($_.Exception.Response) {
                    $status = [int]$_.Exception.Response.StatusCode
                }
                if ($status -ne 404) {
                    throw "Expected HTTP 404, got $status"
                }
            }
            try {
                Invoke-RestMethod -Uri "$ApiBase/api/vehicles/999999/reactivate/" -Method POST -Headers $authHeaders -TimeoutSec 30
                throw 'Expected 404 for missing vehicle'
            } catch {
                $status = $null
                if ($_.Exception.Response) {
                    $status = [int]$_.Exception.Response.StatusCode
                }
                if ($status -ne 404) {
                    throw "Expected HTTP 404, got $status"
                }
            }
        }

        Test-Step "Driver vehicle deactivate route (unauthenticated → 401)" {
            try {
                Invoke-RestMethod -Uri "$ApiBase/api/drivers/me/vehicle/deactivate/" -Method POST -Headers $headers -TimeoutSec 30
                throw 'Expected 401 without token'
            } catch {
                $status = $null
                if ($_.Exception.Response) {
                    $status = [int]$_.Exception.Response.StatusCode
                }
                if ($status -ne 401) {
                    throw "Expected HTTP 401, got $status"
                }
            }
        }
    }
}

Write-Host ""
$summaryColor = if ($script:failed -eq 0) { 'Green' } else { 'Red' }
Write-Host "=== Summary: $($script:passed) passed, $($script:failed) failed ===" -ForegroundColor $summaryColor
if ($script:failed -gt 0) { exit 1 }
