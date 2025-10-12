Write-Host "`n🧹 Commercial-View Repository Cleanup" -ForegroundColor Cyan
Write-Host "Cleaning Python cache and temporary files..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$cleanupReport = @{
    'pycache_removed'      = 0
    'pyc_files_removed'    = 0
    'pytest_cache_removed' = 0
    'space_freed_mb'       = 0
}

# Function to get directory size
function Get-DirectorySize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        return [math]::Round($size / 1MB, 2)
    }
    return 0
}

# Clean __pycache__ directories
Write-Host "`n🗑️  Step 1: Removing __pycache__ directories..." -ForegroundColor Yellow

Get-ChildItem -Path . -Directory -Recurse -Force -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    $size = Get-DirectorySize $_.FullName
    try {
        Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Removed: $($_.FullName) (${size}MB)" -ForegroundColor Green
        $cleanupReport['pycache_removed']++
        $cleanupReport['space_freed_mb'] += $size
    }
    catch {
        Write-Host "   ⚠️  Could not remove: $($_.FullName)" -ForegroundColor Yellow
    }
}

# Clean .pyc files
Write-Host "`n🗑️  Step 2: Removing .pyc files..." -ForegroundColor Yellow

Get-ChildItem -Path . -File -Recurse -Force -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $size = [math]::Round($_.Length / 1KB, 2)
        Remove-Item -Path $_.FullName -Force -ErrorAction Stop
        Write-Host "   ✅ Removed: $($_.Name) (${size}KB)" -ForegroundColor Green
        $cleanupReport['pyc_files_removed']++
    }
    catch {
        Write-Host "   ⚠️  Could not remove: $($_.Name)" -ForegroundColor Yellow
    }
}

# Clean .pytest_cache directories
Write-Host "`n🗑️  Step 3: Removing .pytest_cache directories..." -ForegroundColor Yellow

Get-ChildItem -Path . -Directory -Recurse -Force -Filter ".pytest_cache" -ErrorAction SilentlyContinue | ForEach-Object {
    $size = Get-DirectorySize $_.FullName
    try {
        Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Removed: $($_.FullName) (${size}MB)" -ForegroundColor Green
        $cleanupReport['pytest_cache_removed']++
        $cleanupReport['space_freed_mb'] += $size
    }
    catch {
        Write-Host "   ⚠️  Could not remove: $($_.FullName)" -ForegroundColor Yellow
    }
}

# Clean .ipynb_checkpoints
Write-Host "`n🗑️  Step 4: Removing .ipynb_checkpoints..." -ForegroundColor Yellow

Get-ChildItem -Path . -Directory -Recurse -Force -Filter ".ipynb_checkpoints" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Removed: $($_.FullName)" -ForegroundColor Green
    }
    catch {
        Write-Host "   ⚠️  Could not remove: $($_.FullName)" -ForegroundColor Yellow
    }
}

# Clean .DS_Store files (macOS)
Write-Host "`n🗑️  Step 5: Removing .DS_Store files..." -ForegroundColor Yellow

Get-ChildItem -Path . -File -Recurse -Force -Filter ".DS_Store" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        Remove-Item -Path $_.FullName -Force -ErrorAction Stop
        Write-Host "   ✅ Removed: $($_.FullName)" -ForegroundColor Green
    }
    catch {
        Write-Host "   ⚠️  Could not remove: $($_.FullName)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "📊 CLEANUP SUMMARY" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ("=" * 50) -ForegroundColor Cyan

Write-Host "`n✅ Cleanup Complete!" -ForegroundColor Green
Write-Host "   • __pycache__ directories removed: $($cleanupReport['pycache_removed'])" -ForegroundColor Cyan
Write-Host "   • .pyc files removed: $($cleanupReport['pyc_files_removed'])" -ForegroundColor Cyan
Write-Host "   • .pytest_cache directories removed: $($cleanupReport['pytest_cache_removed'])" -ForegroundColor Cyan
Write-Host "   • Total space freed: $([math]::Round($cleanupReport['space_freed_mb'], 2))MB" -ForegroundColor Cyan

Write-Host "`n💡 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Run: git status" -ForegroundColor White
Write-Host "   2. Verify .gitignore is updated" -ForegroundColor White
Write-Host "   3. Commit cleanup: git add .gitignore && git commit -m 'chore: Clean cache files and update .gitignore'" -ForegroundColor White
Write-Host "   4. Push: git push origin main" -ForegroundColor White

Write-Host "`n🎯 Repository Status: CLEAN ✅" -ForegroundColor Green
