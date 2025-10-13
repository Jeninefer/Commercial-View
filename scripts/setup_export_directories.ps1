#
# Script: setup_export_directories.ps1
# Purpose: Create export directory structure with .gitkeep files
# 

# Define the base path for exports
# Use the current location as the base path since we'll run from the repository root
$basePath = Join-Path -Path $PWD -ChildPath "abaco_runtime/exports"
$basePath = [System.IO.Path]::GetFullPath($basePath)

Write-Host "Creating export directories at: $basePath" -ForegroundColor Cyan

# Create the base directory if it doesn't exist
if (-not (Test-Path $basePath)) {
    New-Item -Path $basePath -ItemType Directory -Force | Out-Null
    Write-Host "Created base directory: $basePath" -ForegroundColor Green
} else {
    Write-Host "Base directory already exists: $basePath" -ForegroundColor Yellow
}

# Create each subdirectory
$directories = @(
    "analytics",
    "dpd",
    "kpi",
    "kpi/json",
    "pricing"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path -Path $basePath -ChildPath $dir
    
    if (-not (Test-Path $fullPath)) {
        New-Item -Path $fullPath -ItemType Directory -Force | Out-Null
        Write-Host "Created directory: $fullPath" -ForegroundColor Green
    } else {
        Write-Host "Directory already exists: $fullPath" -ForegroundColor Yellow
    }
    
    # Add .gitkeep to each directory
    $gitkeepPath = Join-Path -Path $fullPath -ChildPath ".gitkeep"
    if (-not (Test-Path $gitkeepPath)) {
        "# Keep directory structure" | Out-File -FilePath $gitkeepPath -Encoding utf8
        Write-Host "Added .gitkeep to: $fullPath" -ForegroundColor Cyan
    } else {
        Write-Host ".gitkeep already exists in: $fullPath" -ForegroundColor Yellow
    }
}

# Add a .gitkeep to the base exports directory too
$baseGitkeepPath = Join-Path -Path $basePath -ChildPath ".gitkeep"
if (-not (Test-Path $baseGitkeepPath)) {
    "# Keep directory structure" | Out-File -FilePath $baseGitkeepPath -Encoding utf8
    Write-Host "Added .gitkeep to base exports directory" -ForegroundColor Cyan
}

Write-Host "`n✅ Export directory structure created successfully!" -ForegroundColor Green
Write-Host "Directory structure:" -ForegroundColor Cyan
Write-Host "abaco_runtime/exports/.gitkeep" -ForegroundColor White
foreach ($dir in $directories) {
    Write-Host "abaco_runtime/exports/$dir/.gitkeep" -ForegroundColor White
}

