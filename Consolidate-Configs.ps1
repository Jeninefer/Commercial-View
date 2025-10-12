Write-Host "`n📁 Configuration Consolidation Script" -ForegroundColor Cyan
Write-Host "Consolidating configs/ into config/" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$consolidationReport = @{
    'files_moved'      = 0
    'files_skipped'    = 0
    'files_duplicates' = 0
}

# Create config directory if it doesn't exist
if (-not (Test-Path "config")) {
    New-Item -ItemType Directory -Path "config" -Force | Out-Null
    Write-Host "✅ Created config/ directory" -ForegroundColor Green
}

# Check if configs directory exists
if (Test-Path "configs") {
    Write-Host "`n📦 Processing files from configs/..." -ForegroundColor Yellow
    
    $configFiles = Get-ChildItem -Path "configs" -File -ErrorAction SilentlyContinue
    
    foreach ($file in $configFiles) {
        $destPath = Join-Path "config" $file.Name
        
        if (Test-Path $destPath) {
            Write-Host "   ⚠️  Already exists: $($file.Name) (skipping)" -ForegroundColor Yellow
            $consolidationReport['files_duplicates']++
        }
        else {
            try {
                Copy-Item -Path $file.FullName -Destination $destPath -Force
                Write-Host "   ✅ Moved: $($file.Name)" -ForegroundColor Green
                $consolidationReport['files_moved']++
            }
            catch {
                Write-Host "   ❌ Failed to move: $($file.Name)" -ForegroundColor Red
                $consolidationReport['files_skipped']++
            }
        }
    }
}
else {
    Write-Host "`n✅ configs/ directory doesn't exist (already consolidated)" -ForegroundColor Green
}

# Create export directories
Write-Host "`n📁 Creating export directory structure..." -ForegroundColor Yellow

$exportDirs = @(
    "abaco_runtime/exports/abaco",
    "abaco_runtime/exports/analytics",
    "abaco_runtime/exports/buckets",
    "abaco_runtime/exports/dpd",
    "abaco_runtime/exports/kpi",
    "abaco_runtime/exports/pricing",
    "backups"
)

foreach ($dir in $exportDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        # Create .gitkeep file
        New-Item -ItemType File -Path (Join-Path $dir ".gitkeep") -Force | Out-Null
        Write-Host "   ✅ Created: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "   ✓ Exists: $dir" -ForegroundColor Gray
    }
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "📊 CONSOLIDATION SUMMARY" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n✅ Configuration Consolidation Complete!" -ForegroundColor Green
Write-Host "   • Files moved: $($consolidationReport['files_moved'])" -ForegroundColor Cyan
Write-Host "   • Files skipped: $($consolidationReport['files_skipped'])" -ForegroundColor Cyan
Write-Host "   • Duplicates found: $($consolidationReport['files_duplicates'])" -ForegroundColor Cyan

Write-Host "`n📂 Directory Structure:" -ForegroundColor Yellow
Write-Host "   • config/ - Main configuration directory ✅" -ForegroundColor Green
Write-Host "   • abaco_runtime/exports/ - Export directories created ✅" -ForegroundColor Green
Write-Host "   • backups/ - Backup directory created ✅" -ForegroundColor Green

Write-Host "`n💡 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Review consolidated config/ directory" -ForegroundColor White
Write-Host "   2. Delete old configs/ directory if consolidation looks good" -ForegroundColor White
Write-Host "   3. Update import statements to use config/ instead of configs/" -ForegroundColor White
Write-Host "   4. Commit changes: git add config/ .gitignore" -ForegroundColor White

Write-Host "`n🎯 Status: CONFIGURATION CONSOLIDATED ✅" -ForegroundColor Green
