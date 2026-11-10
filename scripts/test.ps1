# Test Script — Code Intelligence Studio
$ErrorActionPreference = "Stop"

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendDir = Join-Path $rootDir "backend"
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    $venvPython = "python"
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Running Code Intelligence Studio Tests" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Push-Location $backendDir
try {
    & $venvPython -m pytest tests/ -v
} finally {
    Pop-Location
}
