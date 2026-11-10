# Health Check Script — Code Intelligence Studio
$ErrorActionPreference = "SilentlyContinue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Code Intelligence Studio Telemetry Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check Backend API
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 3
    Write-Host "[OK] Backend Service: $($res.status) ($($res.service))" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Backend Service offline at http://127.0.0.1:8000" -ForegroundColor Red
}

# 2. Check Database File
$dbFile = "C:\Users\devga\OneDrive\Desktop\CodeIntelligenceStudio\data\codeintel.db"
if (Test-Path $dbFile) {
    $size = (Get-Item $dbFile).Length
    Write-Host "[OK] SQLite Database: codeintel.db exists ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "[NOTICE] SQLite Database not yet initialized on disk." -ForegroundColor Yellow
}

# 3. Check ChromaDB Store
$chromaDir = "C:\Users\devga\OneDrive\Desktop\CodeIntelligenceStudio\data\chroma"
if (Test-Path $chromaDir) {
    Write-Host "[OK] ChromaDB Store: data/chroma ready" -ForegroundColor Green
} else {
    Write-Host "[NOTICE] ChromaDB directory initialized on first indexing." -ForegroundColor Yellow
}

# 4. Check GitHub Authentication
$ghStatus = gh auth status 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] GitHub Auth: Logged in and ready" -ForegroundColor Green
} else {
    Write-Host "[WARN] GitHub Auth: Not authenticated via gh CLI" -ForegroundColor Yellow
}
