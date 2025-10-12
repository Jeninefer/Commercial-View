<#
.SYNOPSIS
Cross-Platform PowerShell Environment Manager for Commercial-View Abaco Integration
.DESCRIPTION
Manages virtual environment and runs Abaco integration for 48,853 record processing
Supports both Windows and macOS PowerShell environments
Spanish Clients | USD Factoring | $208,192,588.65 Portfolio
#>

param(
    [string]$ScriptToRun = "",
    [switch]$UpgradeUV
)

# PowerShell colors and cross-platform detection
Write-Host "🚀 Commercial-View PowerShell Manager (Cross-Platform)" -ForegroundColor Cyan
Write-Host "48,853 Records | Spanish Clients | USD Factoring | $208M+ Portfolio" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Blue

# Detect operating system
$isMacOS = $PSVersionTable.OS -like "*Darwin*" -or $env:HOME -ne $null
$isWindows = $PSVersionTable.Platform -eq "Win32NT" -or $env:USERPROFILE -ne $null

Write-Host "🔍 Detected OS: $(if($isMacOS){'macOS'}elseif($isWindows){'Windows'}else{'Linux/Unix'})" -ForegroundColor Blue

# Navigate to script directory
Set-Location $PSScriptRoot
Write-Host "📁 Project Directory: $(Get-Location)" -ForegroundColor Blue

# Define cross-platform paths
if ($isMacOS) {
    $pythonCmd = "python3"
    $venvPython = "./.venv/bin/python"
    $venvPip = "./.venv/bin/pip"
    $venvActivate = "./.venv/bin/activate"  # For reference only
} else {
    $pythonCmd = "python"
    $venvPython = ".\.venv\Scripts\python.exe"
    $venvPip = ".\.venv\Scripts\pip.exe"
    $venvActivate = ".\.venv\Scripts\Activate.ps1"
}

Write-Host "🔧 Using paths for $(if($isMacOS){'macOS'}else{'Windows'}): $venvPython" -ForegroundColor Gray

# Check for upgrade request
if ($UpgradeUV) {
    Write-Host "🔧 UV upgrade not implemented in PowerShell. Using pip instead." -ForegroundColor Yellow
}

# Check Python installation
Write-Host "`n🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    if ($isMacOS) {
        $pythonVersion = & python3 --version 2>$null
        if ($pythonVersion) {
            Write-Host "✅ Python3 (macOS): $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python3 not found"
        }
    } else {
        $pythonVersion = & python --version 2>$null
        if ($pythonVersion) {
            Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        } else {
            # Try py launcher on Windows
            $pythonVersion = & py --version 2>$null
            if ($pythonVersion) {
                Write-Host "✅ Python (py launcher): $pythonVersion" -ForegroundColor Green
                $pythonCmd = "py"
            } else {
                throw "Python not found"
            }
        }
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    if ($isMacOS) {
        Write-Host "💡 Install with: brew install python" -ForegroundColor Yellow
        Write-Host "💡 Or download from: https://python.org/downloads/" -ForegroundColor Yellow
    } else {
        Write-Host "💡 Download from: https://python.org/downloads/" -ForegroundColor Yellow
    }
    exit 1
}

# Check if virtual environment exists
$venvExists = Test-Path $venvPython
if (-not $venvExists) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "📦 Creating new virtual environment..." -ForegroundColor Yellow
    
    try {
        & $pythonCmd -m venv .venv
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Write-Host "💡 Ensure Python is installed and in PATH" -ForegroundColor Yellow
        exit 1
    }
}

# Test virtual environment
if (Test-Path $venvPython) {
    Write-Host "✅ Virtual environment found: $venvPython" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment creation failed" -ForegroundColor Red
    exit 1
}

# Check for required packages
Write-Host "📦 Checking required packages for Abaco integration..." -ForegroundColor Yellow
try {
    & $venvPython -c "import pandas, numpy, fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Missing packages"
    }
    Write-Host "✅ All required packages available" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing required packages for 48,853 records..." -ForegroundColor Yellow
    & $venvPip install --upgrade pip
    & $venvPip install fastapi uvicorn pandas numpy pyyaml requests
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Packages installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Package installation failed" -ForegroundColor Red
        exit 1
    }
}

# Install from requirements.txt if exists
if (Test-Path "requirements.txt") {
    Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    & $venvPip install -r requirements.txt
}

Write-Host "✅ Environment is ready for Abaco integration!" -ForegroundColor Green

# Execute the requested Python file
if ($ScriptToRun -and $ScriptToRun -ne "--upgrade-uv") {
    Write-Host "🚀 Running: $venvPython $ScriptToRun" -ForegroundColor Blue
    & $venvPython $ScriptToRun
} else {
    Write-Host "`n📋 Available Python scripts for Abaco integration:" -ForegroundColor Yellow
    Get-ChildItem -Name "*.py" | Where-Object { $_ -notlike ".*" } | Sort-Object | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
    
    Write-Host "`n💡 Cross-Platform PowerShell commands available:" -ForegroundColor Yellow
    Write-Host "  .\run_correctly.ps1 server_control.py    # Start Abaco API server" -ForegroundColor Cyan
    Write-Host "  .\run_correctly.ps1 portfolio.py         # Process 48,853 records" -ForegroundColor Cyan
    Write-Host "  .\run_correctly.ps1 path\to\script.py    # Run specific script" -ForegroundColor Cyan
    
    Write-Host "`n🔧 Direct commands for your platform:" -ForegroundColor Yellow
    Write-Host "  $venvPython server_control.py  # Direct execution" -ForegroundColor Cyan
    Write-Host "  $venvPip list                  # List packages" -ForegroundColor Cyan
    Write-Host "  $venvPython --version          # Check Python version" -ForegroundColor Cyan
}

Write-Host "`n🎉 Commercial-View $(if($isMacOS){'macOS'}else{'Windows'}) PowerShell environment ready!" -ForegroundColor Green
