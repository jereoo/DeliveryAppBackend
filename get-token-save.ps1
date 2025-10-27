# get-token-save.ps1

$Username = "admin"
$Password = "w3r3w0lf"
$Url = "http://192.168.1.85:8081/api/token/"

$Body = @{
    username = $Username
    password = $Password
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $Url -Method Post -ContentType "application/json" -Body $Body

Write-Host "Access Token:" $response.access -ForegroundColor Green
Write-Host "Refresh Token:" $response.refresh -ForegroundColor Yellow

# Save access token to file for later use
$response.access | Out-File -FilePath ".\last-token.txt" -Encoding ascii
