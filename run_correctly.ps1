<#
.SYNOPSIS
PowerShell Environment Manager for Commercial-View Abaco Integration
.DESCRIPTION
Manages virtual environment and runs Abaco integration for 48,853 record processing
Spanish Clients | USD Factoring | $208,192,588.65 Portfolio
#>

# PowerShell colors
$Colors = @{
    Red = 'Red'
    Green = 'Green' 
    Yellow = 'Yellow'
    Blue = 'Blue'
    Cyan = 'Cyan'
}

# Navigate to script directory
Set-Location $PSScriptRoot
Write-Host "📁 Project Directory: $(Get-Location)" -ForegroundColor $Colors.Blue

# Check for upgrade request
if ($args[0] -eq "--upgrade-uv" -or $args[0] -eq "--uv-upgrade") {
    Write-Host "🔧 PowerShell UV upgrade not implemented. Using pip instead." -ForegroundColor $Colors.Yellow
}

# Check if virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor $Colors.Red
    Write-Host "📦 Creating new virtual environment..." -ForegroundColor $Colors.Yellow
    
    try {
        python -m venv .venv
        Write-Host "✅ Virtual environment created" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor $Colors.Red
        Write-Host "💡 Ensure Python is installed and in PATH" -ForegroundColor $Colors.Yellow
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor $Colors.Yellow
try {
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated successfully" -ForegroundColor $Colors.Green
} catch {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor $Colors.Red
    Write-Host "💡 Try: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor $Colors.Yellow
    exit 1
}

# Check for required packages
Write-Host "📦 Checking required packages for Abaco integration..." -ForegroundColor $Colors.Yellow
try {
    & ".\.venv\Scripts\python.exe" -c "import pandas, numpy, fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Missing packages"
    }
    Write-Host "✅ All required packages available" -ForegroundColor $Colors.Green
} catch {
    Write-Host "📦 Installing required packages for 48,853 records..." -ForegroundColor $Colors.Yellow
    & ".\.venv\Scripts\pip.exe" install fastapi uvicorn pandas numpy pyyaml requests
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Packages installed successfully" -ForegroundColor $Colors.Green
    } else {
        Write-Host "❌ Package installation failed" -ForegroundColor $Colors.Red
        exit 1
    }
}

# Install from requirements.txt if exists
if (Test-Path "requirements.txt") {
    Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor $Colors.Yellow
    & ".\.venv\Scripts\pip.exe" install -r requirements.txt
}

Write-Host "✅ Environment is ready for Abaco integration!" -ForegroundColor $Colors.Green

# Execute the requested Python file
if ($args[0] -and $args[0] -ne "--upgrade-uv") {
    Write-Host "🚀 Running: python $($args[0])" -ForegroundColor $Colors.Blue
    & ".\.venv\Scripts\python.exe" $args[0]
} else {
    Write-Host "📋 Available Python scripts for Abaco integration:" -ForegroundColor $Colors.Yellow
    Get-ChildItem -Name "*.py" | Where-Object { $_ -notlike ".*" } | Sort-Object
    
    Write-Host "`n💡 Commands available:" -ForegroundColor $Colors.Yellow
    Write-Host "  .\run_correctly.ps1 server_control.py    # Start Abaco API server" -ForegroundColor $Colors.Cyan
    Write-Host "  .\run_correctly.ps1 portfolio.py         # Process 48,853 records" -ForegroundColor $Colors.Cyan
    Write-Host "  .\run_correctly.ps1 path\to\script.py    # Run specific script" -ForegroundColor $Colors.Cyan
}
