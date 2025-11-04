$ErrorActionPreference = "Stop"

$py = ".\.venv\Scripts\python.exe"
if (-Not (Test-Path $py)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    $py = ".\.venv\Scripts\python.exe"
}

Write-Host "Installing dashboard dependencies..." -ForegroundColor Cyan
& $py -m pip install -r .\pv_annotation\requirements.txt --no-input

Write-Host "Starting Priority Vehicle Annotation (port 5600)..." -ForegroundColor Green
Start-Process $py "-m flask --app pv_annotation.app run --host 0.0.0.0 --port 5600"

Start-Sleep -Seconds 2
Write-Host "Opening http://127.0.0.1:5600" -ForegroundColor Yellow
Start-Process "http://127.0.0.1:5600"

Write-Host "Dashboard started." -ForegroundColor Cyan

