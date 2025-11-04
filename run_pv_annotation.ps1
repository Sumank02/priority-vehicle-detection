# Requires PowerShell
# Usage: powershell -ExecutionPolicy Bypass -File .\run_pv_annotation.ps1

$ErrorActionPreference = "Stop"

$py = ".\.venv\Scripts\python.exe"

if (-Not (Test-Path $py)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}

Write-Host "Installing dashboard dependencies..." -ForegroundColor Cyan
& $py -m pip install -r .\pv_annotation\requirements.txt --disable-pip-version-check

Write-Host "Starting Priority Vehicle Annotation (port 5600)..." -ForegroundColor Green
Start-Process $py ".\pv_annotation\app.py"

Start-Sleep -Seconds 2

Write-Host "Opening http://127.0.0.1:5600" -ForegroundColor Yellow
Start-Process "http://127.0.0.1:5600"

Write-Host "Dashboard started. Check the app window for logs." -ForegroundColor Cyan

