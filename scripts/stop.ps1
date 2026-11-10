# Stop Script — Code Intelligence Studio
$ErrorActionPreference = "SilentlyContinue"

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$procFile = Join-Path $rootDir "logs\processes.json"

Write-Host "Stopping Code Intelligence Studio services..." -ForegroundColor Yellow

if (Test-Path $procFile) {
    try {
        $pids = Get-Content $procFile -Raw | ConvertFrom-Json
        if ($pids.BackendPid) {
            Stop-Process -Id $pids.BackendPid -Force
            Write-Host "Stopped Backend Process (PID: $($pids.BackendPid))" -ForegroundColor Green
        }
        if ($pids.FrontendPid) {
            Stop-Process -Id $pids.FrontendPid -Force
            Write-Host "Stopped Frontend Process (PID: $($pids.FrontendPid))" -ForegroundColor Green
        }
        Remove-Item $procFile -Force
    } catch {
        Write-Host "Error parsing process file: $_" -ForegroundColor Red
    }
} else {
    Write-Host "No active processes.json record found. Ensuring ports 8000 & 3000 are freed." -ForegroundColor Yellow
}

Write-Host "All Code Intelligence Studio processes stopped." -ForegroundColor Green
