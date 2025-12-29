# PowerShell script to enable Windows Long Path Support
# MUST RUN AS ADMINISTRATOR

Write-Host "Checking current Long Path setting..." -ForegroundColor Yellow

$currentValue = (Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -ErrorAction SilentlyContinue).LongPathsEnabled

if ($currentValue -eq 1) {
    Write-Host "✅ Long Path Support is already enabled!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Long Path Support is currently disabled." -ForegroundColor Red
    Write-Host "Attempting to enable Long Path Support..." -ForegroundColor Yellow
    
    try {
        New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force | Out-Null
        Write-Host "✅ Long Path Support has been enabled!" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANT: You MUST restart your computer for this to take effect." -ForegroundColor Yellow
        Write-Host "After restarting, run: pip install -r requirements.txt" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ Failed to enable Long Path Support. Error: $_" -ForegroundColor Red
        Write-Host "Make sure you're running PowerShell as Administrator!" -ForegroundColor Yellow
    }
}

