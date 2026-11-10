# Start Script — Code Intelligence Studio
$ErrorActionPreference = "Stop"

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    $venvPython = "python"
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Launching Code Intelligence Studio" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Start Backend in Background
Write-Host "Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath $venvPython -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $backendDir -PassThru

# 2. Start Frontend in Background (Using cmd.exe to invoke npm.cmd cleanly on Windows)
Write-Host "Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Yellow
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run start" -WorkingDirectory $frontendDir -PassThru

# Save PIDs to logs for clean stopping
$pids = @{
    BackendPid = $backendProcess.Id
    FrontendPid = $frontendProcess.Id
    StartedAt = (Get-Date).ToString("o")
}
$pids | ConvertTo-Json | Out-File (Join-Path $rootDir "logs\processes.json") -Encoding utf8

Start-Sleep -Seconds 3

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host " Code Intelligence Studio is RUNNING!" -ForegroundColor Green
Write-Host " Web Dashboard:  http://localhost:3000" -ForegroundColor Cyan
Write-Host " Backend API:    http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host " OpenAPI Docs:   http://127.0.0.1:8000/api/v1/docs" -ForegroundColor Cyan
Write-Host " Stop Command:   .\scripts\stop.ps1" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green
