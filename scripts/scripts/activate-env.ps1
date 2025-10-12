# PowerShell script to properly activate the virtual environment
# and make Python tools available in the current session

$ErrorActionPreference = "Stop"

# Function to check if command exists
function Test-Command {
    param($command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    try { 
        if (Get-Command $command) { return $true }
    }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
    return $false
}

Write-Host "Activating Commercial View virtual environment..." -ForegroundColor Cyan

$venvPath = Join-Path $PSScriptRoot ".venv"
$activateScript = Join-Path $venvPath "Scripts" "Activate.ps1"

# Check if we're on Windows or Unix-like system
if (Test-Path $activateScript) {
    # Windows style activation
    Write-Host "Using Windows-style activation" -ForegroundColor Green
    . $activateScript
} else {
    $activateScript = Join-Path $venvPath "bin" "Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Host "Using Unix-style activation" -ForegroundColor Green
        . $activateScript
    } else {
        Write-Host "Error: Virtual environment activation script not found!" -ForegroundColor Red
        Write-Host "Expected at: $activateScript" -ForegroundColor Red
        Write-Host "Do you need to create the virtual environment first?" -ForegroundColor Yellow
        Write-Host "Try: python -m venv .venv" -ForegroundColor Yellow
        exit 1
    }
}

# Verify python is accessible
if (Test-Command python) {
    $pythonVersion = python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
    Write-Host "✅ $pythonVersion activated" -ForegroundColor Green
    
    # Check for pandas
    python -c "import pandas; print(f'✅ pandas {pandas.__version__} installed')" -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ pandas not installed. Run: pip install pandas" -ForegroundColor Yellow
    }
    
    # Check for pytest
    python -c "import pytest; print(f'✅ pytest {pytest.__version__} installed')" -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ pytest not installed. Run: pip install pytest" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Python still not found in PATH after activation" -ForegroundColor Red
    exit 1
}

Write-Host "`nEnvironment activated. Common commands:" -ForegroundColor Cyan
Write-Host "  python run.py                  # Run the application" -ForegroundColor White
Write-Host "  python -m pytest               # Run tests" -ForegroundColor White
Write-Host "  python src/utils/schema_converter.py /Users/jenineferderas/Downloads/abaco_schema_autodetected.json --output src/models/" -ForegroundColor White
Write-Host "  pip install -r requirements.txt # Install dependencies" -ForegroundColor White
