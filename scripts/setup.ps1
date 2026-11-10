# Setup Script — Code Intelligence Studio
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Initializing Code Intelligence Studio" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$cliDir = Join-Path $rootDir "cli"

# 1. Initialize Directories
$dirs = @("data", "workspaces", "artifacts", "logs", "backups")
foreach ($d in $dirs) {
    $p = Join-Path $rootDir $d
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Force -Path $p | Out-Null
    }
}
Write-Host "[OK] Runtime storage directories initialized." -ForegroundColor Green

# 2. Setup Python Virtual Environment in backend
$venvPath = Join-Path $backendDir ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating Python virtual environment in backend/.venv..." -ForegroundColor Yellow
    python -m venv $venvPath
}
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

Write-Host "Upgrading pip and installing core backend dependencies..." -ForegroundColor Yellow
& $pipExe install --upgrade pip --quiet
& $pipExe install -e $backendDir --quiet
& $pipExe install -e $cliDir --quiet
Write-Host "[OK] Backend & CLI dependencies installed." -ForegroundColor Green

# 3. Setup Frontend npm packages
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location $frontendDir
try {
    npm install --quiet
    Write-Host "[OK] Frontend packages installed." -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host "`nSetup completed successfully! Run .\scripts\start.ps1 to start services." -ForegroundColor Green
