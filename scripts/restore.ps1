# Restore Script — Code Intelligence Studio
param (
    [Parameter(Mandatory=$true)]
    [string]$BackupPath
)

$ErrorActionPreference = "Stop"
$rootDir = "C:\Users\devga\OneDrive\Desktop\CodeIntelligenceStudio"

if (-not (Test-Path $BackupPath)) {
    Write-Host "[FAIL] Backup path '$BackupPath' does not exist." -ForegroundColor Red
    exit 1
}

Write-Host "Restoring data from $BackupPath..." -ForegroundColor Yellow

$backupDb = Join-Path $BackupPath "codeintel.db"
if (Test-Path $backupDb) {
    Copy-Item $backupDb -Destination (Join-Path $rootDir "data\codeintel.db") -Force
    Write-Host "[OK] SQLite database restored." -ForegroundColor Green
}

$backupChroma = Join-Path $BackupPath "chroma"
if (Test-Path $backupChroma) {
    Copy-Item $backupChroma -Destination (Join-Path $rootDir "data\chroma") -Recurse -Force
    Write-Host "[OK] ChromaDB vector collection restored." -ForegroundColor Green
}

Write-Host "Restore operation completed successfully." -ForegroundColor Green
