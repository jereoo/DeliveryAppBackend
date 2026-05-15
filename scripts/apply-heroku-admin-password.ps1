# Apply Heroku Config Var ADMIN_PASSWORD to the Django admin user in the database.
# Run on your machine after `heroku login` (Cursor may not have Heroku auth).

param(
    [string]$App = 'truck-buddy'
)

$ErrorActionPreference = 'Stop'

Write-Host "Checking Heroku login..." -ForegroundColor Cyan
heroku auth:whoami
if ($LASTEXITCODE -ne 0) {
    Write-Host "Run: heroku login" -ForegroundColor Red
    exit 1
}

Write-Host "Running ensure_admin on $App (loads ADMIN_PASSWORD from config)..." -ForegroundColor Cyan
heroku run python manage.py ensure_admin -a $App
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Done. Test login: POST .../api/token/ on your app's Heroku URL with username + ADMIN_PASSWORD from config." -ForegroundColor Green
