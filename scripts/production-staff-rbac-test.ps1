# Phase 4G — production staff RBAC smoke test (API + mobile nav matrix).
# Usage:
#   $env:ADMIN_PASSWORD = "<Heroku ADMIN_PASSWORD>"
#   .\scripts\production-staff-rbac-test.ps1
#
# Creates idempotent prod.test.* staff users (password: ProdStaffTest1!) if missing.

param(
    [string]$ApiBase = $(if ($env:API_BASE_URL) { $env:API_BASE_URL.TrimEnd('/') } else { 'https://truck-buddy-f14f250ae8b3.herokuapp.com' }),
    [string]$WebUrl = $(if ($env:WEB_URL) { $env:WEB_URL } else { 'https://deliveryapp-mobile.vercel.app' }),
    [string]$AdminUser = $(if ($env:ADMIN_USERNAME) { $env:ADMIN_USERNAME } else { 'admin' }),
    [string]$AdminPassword = $env:ADMIN_PASSWORD,
    [string]$StaffTestPassword = 'ProdStaffTest1!'
)

$ErrorActionPreference = 'Stop'
$script:failed = 0
$script:passed = 0

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

function Get-Token {
    param([string]$Username, [string]$Password)
    $body = @{ username = $Username; password = $Password } | ConvertTo-Json
    $t = Invoke-RestMethod -Uri "$ApiBase/api/token/" -Method POST -Body $body -Headers @{ 'Content-Type' = 'application/json' } -TimeoutSec 30
    if (-not $t.access) { throw 'No access token' }
    return $t.access
}

function Get-Me {
    param([string]$Token)
    return Invoke-RestMethod -Uri "$ApiBase/api/me/" -Method GET -Headers @{
        Authorization = "Bearer $Token"
    } -TimeoutSec 30
}

function Invoke-Api {
    param(
        [string]$Token,
        [string]$Method,
        [string]$Path,
        [object]$Body = $null,
        [int[]]$ExpectStatus = @(200)
    )
    $headers = @{ Authorization = "Bearer $Token"; 'Content-Type' = 'application/json' }
    try {
        if ($Body) {
            $json = $Body | ConvertTo-Json -Depth 6
            return Invoke-WebRequest -Uri "$ApiBase$Path" -Method $Method -Headers $headers -Body $json -TimeoutSec 30 -UseBasicParsing
        }
        return Invoke-WebRequest -Uri "$ApiBase$Path" -Method $Method -Headers $headers -TimeoutSec 30 -UseBasicParsing
    } catch {
        $resp = $_.Exception.Response
        if ($resp -and ($ExpectStatus -contains [int]$resp.StatusCode)) {
            return $resp
        }
        $status = if ($resp) { [int]$resp.StatusCode } else { 'n/a' }
        throw "HTTP $status for $Method $Path (expected $($ExpectStatus -join '/'))"
    }
}

function Test-NavMatrix {
    param(
        [string]$Label,
        [object]$Me,
        [hashtable]$ExpectedScreens,
        [hashtable]$ExpectedDeniedScreens
    )
    $perms = @($Me.permissions)
    $role = $Me.role
    foreach ($entry in $ExpectedScreens.GetEnumerator()) {
        $screen = $entry.Key
        $required = @($entry.Value)
        $allowed = $false
        if ($role -eq 'admin') { $allowed = $true }
        elseif ($role -eq 'staff') {
            foreach ($code in $required) {
                if ($perms -contains $code) { $allowed = $true; break }
            }
        }
        if (-not $allowed) {
            throw "$Label nav: expected access to $screen"
        }
    }
    foreach ($entry in $ExpectedDeniedScreens.GetEnumerator()) {
        $screen = $entry.Key
        $required = @($entry.Value)
        $allowed = $false
        if ($role -eq 'admin') { $allowed = $true }
        elseif ($role -eq 'staff') {
            foreach ($code in $required) {
                if ($perms -contains $code) { $allowed = $true; break }
            }
        }
        if ($allowed) {
            throw "$Label nav: should NOT access $screen"
        }
    }
}

$StaffAccounts = @(
    @{ Username = 'prod.test.ops'; Role = 'operations_admin'; Email = 'prod.test.ops@example.com' },
    @{ Username = 'prod.test.reviewer'; Role = 'compliance_reviewer'; Email = 'prod.test.reviewer@example.com' },
    @{ Username = 'prod.test.readonly'; Role = 'read_only'; Email = 'prod.test.readonly@example.com' }
)

Write-Host "Phase 4G staff RBAC prod test" -ForegroundColor Yellow
Write-Host "API: $ApiBase"
Write-Host "Web: $WebUrl"

Test-Step "API health" {
    $r = Invoke-RestMethod -Uri "$ApiBase/api/health/" -TimeoutSec 30
    if ($r.status -ne 'ok') { throw 'health not ok' }
}

Test-Step "Staff API requires auth (401)" {
    try {
        Invoke-RestMethod -Uri "$ApiBase/api/staff/" -TimeoutSec 30
        throw 'Expected 401'
    } catch {
        if ([int]$_.Exception.Response.StatusCode -ne 401) { throw $_ }
    }
}

Test-Step "Vercel bundle includes staff RBAC" {
    $html = (Invoke-WebRequest -Uri $WebUrl -UseBasicParsing -TimeoutSec 45).Content
    if ($html -notmatch 'index-.*\.js') { throw 'No bundle script in index.html' }
    $bundlePath = [regex]::Match($html, '(/_expo/static/js/web/index-[^"]+\.js)').Groups[1].Value
    $js = (Invoke-WebRequest -Uri "$WebUrl$bundlePath" -UseBasicParsing -TimeoutSec 60).Content
    foreach ($needle in @('Manage Staff', 'staff.manage', 'Staff Operations', 'canAccessAdminScreen')) {
        if ($js -notmatch [regex]::Escape($needle)) { throw "Missing bundle string: $needle" }
    }
}

if (-not $AdminPassword) {
    Write-Host ""
    Write-Host "Skipping authenticated staff tests - set ADMIN_PASSWORD (Heroku config)." -ForegroundColor Yellow
    Write-Host ""
    $summaryColor = if ($script:failed -eq 0) { 'Green' } else { 'Red' }
    Write-Host "=== Summary: $($script:passed) passed, $($script:failed) failed ===" -ForegroundColor $summaryColor
    exit $(if ($script:failed -gt 0) { 1 } else { 0 })
}

$script:adminToken = $null
Test-Step "Super Admin login + /api/me/" {
    $script:adminToken = Get-Token -Username $AdminUser -Password $AdminPassword
    $me = Get-Me -Token $script:adminToken
    if ($me.role -ne 'admin') { throw "Expected role admin, got $($me.role)" }
    if ($me.staff_role -ne 'super_admin') { throw "Expected staff_role super_admin" }
    if ($me.permissions -notcontains 'staff.manage') { throw 'Missing staff.manage permission' }
}

Test-Step "Super Admin can list staff" {
    $null = Invoke-Api -Token $script:adminToken -Method GET -Path '/api/staff/'
}

foreach ($acct in $StaffAccounts) {
    Test-Step "Ensure staff user $($acct.Username)" {
        $list = Invoke-RestMethod -Uri "$ApiBase/api/staff/" -Headers @{ Authorization = "Bearer $($script:adminToken)" } -TimeoutSec 30
        $existing = @($list) | Where-Object { $_.username -eq $acct.Username } | Select-Object -First 1
        if (-not $existing) {
            $body = @{
                username = $acct.Username
                email = $acct.Email
                password = $StaffTestPassword
                first_name = 'Prod'
                last_name = 'Test'
                staff_role = $acct.Role
                job_title = "Phase 4G $($acct.Role)"
            }
            $null = Invoke-RestMethod -Uri "$ApiBase/api/staff/" -Method POST -Body ($body | ConvertTo-Json) -Headers @{
                Authorization = "Bearer $($script:adminToken)"
                'Content-Type' = 'application/json'
            } -TimeoutSec 30
        }
    }
}

Test-Step "Super Admin nav matrix (all screens)" {
    $me = Get-Me -Token $script:adminToken
    Test-NavMatrix -Label 'super_admin' -Me $me -ExpectedScreens @{
        admin_staff = @('staff.manage')
        admin_compliance = @('reports.view', 'compliance.view')
        admin_deliveries = @('deliveries.view')
    } -ExpectedDeniedScreens @{}
}

$roleTests = @(
    @{
        Username = 'prod.test.readonly'
        Label = 'Read Only'
        ExpectRole = 'staff'
        ExpectStaffRole = 'read_only'
        DenyStaffApi = $true
        DenyPostCustomer = $true
        AllowGetDrivers = $true
        NavAllow = @{
            admin_drivers = @('drivers.view')
            admin_compliance = @('reports.view', 'compliance.view')
        }
        NavDeny = @{ admin_staff = @('staff.manage') }
    },
    @{
        Username = 'prod.test.reviewer'
        Label = 'Compliance Reviewer'
        ExpectRole = 'staff'
        ExpectStaffRole = 'compliance_reviewer'
        DenyStaffApi = $true
        DenyPostCustomer = $true
        AllowGetDrivers = $true
        HasComplianceVerify = $true
        NavAllow = @{
            admin_compliance = @('reports.view', 'compliance.view')
            admin_drivers = @('drivers.view')
        }
        NavDeny = @{ admin_staff = @('staff.manage') }
    },
    @{
        Username = 'prod.test.ops'
        Label = 'Operations Admin'
        ExpectRole = 'staff'
        ExpectStaffRole = 'operations_admin'
        DenyStaffApi = $true
        AllowGetDrivers = $true
        HasDriversApprove = $true
        NavAllow = @{
            admin_drivers = @('drivers.view')
            admin_deliveries = @('deliveries.view')
            admin_compliance = @('reports.view', 'compliance.view')
        }
        NavDeny = @{ admin_staff = @('staff.manage') }
    }
)

foreach ($rt in $roleTests) {
    $token = Get-Token -Username $rt.Username -Password $StaffTestPassword
    Test-Step "$($rt.Label) /api/me/" {
        $me = Get-Me -Token $token
        if ($me.role -ne $rt.ExpectRole) { throw "role=$($me.role)" }
        if ($me.staff_role -ne $rt.ExpectStaffRole) { throw "staff_role=$($me.staff_role)" }
        if ($rt.DenyStaffApi) {
            try {
                Invoke-Api -Token $token -Method GET -Path '/api/staff/' -ExpectStatus @(403,401)
            } catch { throw $_ }
        }
    }
    Test-Step "$($rt.Label) mobile nav matrix" {
        $me = Get-Me -Token $token
        Test-NavMatrix -Label $rt.Label -Me $me -ExpectedScreens $rt.NavAllow -ExpectedDeniedScreens $rt.NavDeny
    }
    if ($rt.AllowGetDrivers) {
        Test-Step "$($rt.Label) can list drivers" {
            $null = Invoke-Api -Token $token -Method GET -Path '/api/drivers/'
        }
    }
    if ($rt.DenyPostCustomer) {
        Test-Step "$($rt.Label) cannot create customer (403)" {
            $null = Invoke-Api -Token $token -Method POST -Path '/api/customers/' -Body @{
                username = 'should_not_create'
                email = 'should_not_create@example.com'
                password = 'ShouldNot1!'
                first_name = 'No'
                last_name = 'Create'
                phone_number = '5559990001'
                address_country = 'US'
            } -ExpectStatus @(403)
        }
    }
}

Write-Host ""
$summaryColor = if ($script:failed -eq 0) { 'Green' } else { 'Red' }
Write-Host "=== Summary: $($script:passed) passed, $($script:failed) failed ===" -ForegroundColor $summaryColor
if ($script:failed -gt 0) { exit 1 }
