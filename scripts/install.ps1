# Auto-freeze script untuk Windows PowerShell
# Cara pakai: .\scripts\install.ps1 package-name
# Contoh: .\scripts\install.ps1 requests

param(
    [Parameter(Mandatory=$true)]
    [string[]]$Packages
)

Write-Host "Installing packages: $($Packages -join ', ')" -ForegroundColor Cyan

# Install package(s)
$installCommand = "pip install $($Packages -join ' ')"
Write-Host "Running: $installCommand" -ForegroundColor Yellow
Invoke-Expression $installCommand

# Check if installation was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nInstallation successful! Updating requirements.txt..." -ForegroundColor Green
    
    # Freeze dependencies to requirements.txt
    pip freeze > requirements.txt
    
    Write-Host "requirements.txt has been updated!" -ForegroundColor Green
    Write-Host "`nNew requirements.txt content:" -ForegroundColor Cyan
    Get-Content requirements.txt | Select-Object -First 10
    Write-Host "... (showing first 10 lines)" -ForegroundColor Gray
} else {
    Write-Host "`nInstallation failed! requirements.txt not updated." -ForegroundColor Red
    exit 1
}
