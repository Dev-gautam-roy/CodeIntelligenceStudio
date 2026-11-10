# Verify Environment Script — Code Intelligence Studio
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Code Intelligence Studio Environment Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python
try {
    $pyVer = python --version 2>&1
    Write-Host "[PASS] Python: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Python runtime not found!" -ForegroundColor Red
}

# Check Node & npm
try {
    $nodeVer = node --version 2>&1
    $npmVer = npm --version 2>&1
    Write-Host "[PASS] Node.js: $nodeVer | npm: $npmVer" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Node.js or npm not found!" -ForegroundColor Red
}

# Check Git
try {
    $gitVer = git --version 2>&1
    Write-Host "[PASS] Git: $gitVer" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Git not found!" -ForegroundColor Red
}

# Check GitHub CLI
try {
    $ghVer = gh --version 2>&1 | Select-Object -First 1
    Write-Host "[PASS] GitHub CLI: $ghVer" -ForegroundColor Green
} catch {
    Write-Host "[WARN] GitHub CLI ('gh') not authenticated or found." -ForegroundColor Yellow
}

# Check Project Directories
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$dirs = @("data", "workspaces", "artifacts", "logs", "backups")
foreach ($d in $dirs) {
    $p = Join-Path $root $d
    if (Test-Path $p) {
        Write-Host "[PASS] Directory: $d exists" -ForegroundColor Green
    } else {
        New-Item -ItemType Directory -Force -Path $p | Out-Null
        Write-Host "[CREATED] Directory: $d initialized" -ForegroundColor Cyan
    }
}

Write-Host "`nEnvironment verification finished successfully." -ForegroundColor Green
