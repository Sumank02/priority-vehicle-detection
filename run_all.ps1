# Requires PowerShell
# Usage: powershell -ExecutionPolicy Bypass -File .\run_all.ps1

$ErrorActionPreference = "Stop"

$py = ".\.venv\Scripts\python.exe"

Write-Host "Installing dependencies..." -ForegroundColor Cyan
& $py -m pip install -r requirements.txt

Write-Host "Starting Traffic Controller (port 5001)..." -ForegroundColor Green
Start-Process $py "-m traffic_controller.traffic_controller"

Start-Sleep -Seconds 1

Write-Host "Starting Server (port 5000)..." -ForegroundColor Green
Start-Process $py "-m server.server"

Start-Sleep -Seconds 1

Write-Host "Starting Dashboard (port 5100)..." -ForegroundColor Green
Start-Process $py "-m dashboard.app"

Start-Sleep -Seconds 2

Write-Host "Starting Scenario Simulator (alternating AMB/FIRT instances)..." -ForegroundColor Green
Start-Process $py "-m vehicle.scenario_sim --min_duration 10 --max_duration 15 --idle 5 --tick 1.0"

Start-Sleep -Seconds 2

Write-Host "Opening Dashboard at http://127.0.0.1:5100" -ForegroundColor Yellow
Start-Process "http://127.0.0.1:5100"

Write-Host "All processes started. Check separate windows for logs." -ForegroundColor Cyan
