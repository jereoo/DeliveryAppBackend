# get-token.ps1
# Run with: .\get-token.ps1

# Config
$Username = "admin"
$Password = "w3r3w0lf"
$Url = "http://127.0.0.1:8000/api/token/"

# Request body as JSON
$Body = @{
    username = $Username
    password = $Password
} | ConvertTo-Json

# Make request
$response = Invoke-RestMethod -Uri $Url -Method Post -ContentType "application/json" -Body $Body

# Print tokens nicely
Write-Host "Access Token:" $response.access -ForegroundColor Green
Write-Host "Refresh Token:" $response.refresh -ForegroundColor Yellow