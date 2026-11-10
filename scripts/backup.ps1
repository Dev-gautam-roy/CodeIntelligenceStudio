# Backup Script — Code Intelligence Studio
$ErrorActionPreference = "Stop"

$rootDir = "C:\Users\devga\OneDrive\Desktop\CodeIntelligenceStudio"
$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$backupDest = Join-Path $rootDir "backups\backup_$timestamp"

New-Item -ItemType Directory -Force -Path $backupDest | Out-Null

Write-Host "Creating snapshot backup at $backupDest..." -ForegroundColor Yellow

# Backup SQLite Database
$db = Join-Path $rootDir "data\codeintel.db"
if (Test-Path $db) {
    Copy-Item $db -Destination (Join-Path $backupDest "codeintel.db")
    Write-Host "[OK] SQLite database copied." -ForegroundColor Green
}

# Backup ChromaDB
$chroma = Join-Path $rootDir "data\chroma"
if (Test-Path $chroma) {
    Copy-Item $chroma -Destination (Join-Path $backupDest "chroma") -Recurse
    Write-Host "[OK] ChromaDB vector collection copied." -ForegroundColor Green
}

Write-Host "Backup completed: $backupDest" -ForegroundColor Green
