<#
.Synopsis
<<<<<<< HEAD
Activate Commercial-View commercial lending development environment for PowerShell session.

.Description
Activates the Python virtual environment and sets up project-specific 
environment variables, paths, and development tools for Commercial-View 
commercial lending platform with enhanced validation and management features.
=======
Activate Commercial-View development environment for PowerShell session.

.Description
Activates the Python virtual environment and sets up project-specific 
environment variables, paths, and development tools for Commercial-View.
>>>>>>> 9039104 (Add missing project files and documentation)

.Parameter SkipDependencyCheck
Skip checking for required Python dependencies.

.Parameter AutoInstall
Automatically install missing dependencies without prompting.

<<<<<<< HEAD
.Parameter Production
Configure environment for production-like settings.

.Parameter Verbose
Enable verbose output for detailed diagnostics.

=======
>>>>>>> 9039104 (Add missing project files and documentation)
.Example
.\scripts\Activate-Project.ps1
Activates the Commercial-View development environment.

.Example
<<<<<<< HEAD
.\scripts\Activate-Project.ps1 -AutoInstall -Verbose
Activates the environment with automatic dependency installation and detailed output.

.Example
.\scripts\Activate-Project.ps1 -Production
Activates the environment with production-like configuration.
=======
.\scripts\Activate-Project.ps1 -AutoInstall
Activates the environment and automatically installs missing dependencies.
>>>>>>> 9039104 (Add missing project files and documentation)
#>

[CmdletBinding()]
param(
    [switch]$SkipDependencyCheck,
<<<<<<< HEAD
    [switch]$AutoInstall,
    [switch]$Production,
    [switch]$Verbose
)

# Enhanced color definitions for comprehensive output
=======
    [switch]$AutoInstall
)

# Color definitions for output
>>>>>>> 9039104 (Add missing project files and documentation)
$Colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
<<<<<<< HEAD
    Magenta = "Magenta"
    White = "White"
    DarkGray = "DarkGray"
=======
>>>>>>> 9039104 (Add missing project files and documentation)
}

function Write-ColorOutput {
    param(
        [string]$Message,
<<<<<<< HEAD
        [string]$Color = "White",
        [switch]$NoNewline
    )
    if ($NoNewline) {
        Write-Host $Message -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Write-Section {
    param([string]$Title)
    Write-ColorOutput "`n$Title" $Colors.Blue
    Write-ColorOutput ("=" * $Title.Length) $Colors.Blue
}

function Test-PythonModule {
    param([string]$ModuleName)
    try {
        & python -c "import $ModuleName" 2>$null
        return $true
    } catch {
        return $false
    }
}

Write-ColorOutput "🏦 Initializing Commercial-View Commercial Lending Platform" $Colors.Blue
Write-ColorOutput ("=" * 60) $Colors.Blue

# Enhanced directory validation
=======
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "🚀 Initializing Commercial-View Development Environment" $Colors.Blue
Write-ColorOutput ("=" * 50) $Colors.Blue

# Check if we're in the correct directory
>>>>>>> 9039104 (Add missing project files and documentation)
if (-not (Test-Path "requirements.txt") -or -not (Test-Path "src")) {
    Write-ColorOutput "❌ Error: Not in Commercial-View project root directory" $Colors.Red
    Write-ColorOutput "Please run this script from the project root directory" $Colors.Red
    exit 1
}

<<<<<<< HEAD
# Validate commercial lending project structure
$requiredPaths = @(
    "configs",
    "src",
    "scripts",
    "docs"
)

$missingPaths = @()
foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        $missingPaths += $path
    }
}

if ($missingPaths) {
    Write-ColorOutput "⚠️  Missing project directories: $($missingPaths -join ', ')" $Colors.Yellow
}

# Enhanced virtual environment management
if (-not (Test-Path ".venv")) {
    Write-ColorOutput "⚠️  Virtual environment not found. Creating..." $Colors.Yellow
    try {
        & python -m venv .venv
        Write-ColorOutput "✅ Virtual environment created successfully" $Colors.Green
    } catch {
        Write-ColorOutput "❌ Failed to create virtual environment: $($_.Exception.Message)" $Colors.Red
        exit 1
    }
}

# Activate virtual environment with error handling
Write-ColorOutput "📦 Activating virtual environment..." $Colors.Green
try {
    & ".\.venv\Scripts\Activate.ps1"
    Write-ColorOutput "✅ Virtual environment activated" $Colors.Green
} catch {
    Write-ColorOutput "❌ Failed to activate virtual environment: $($_.Exception.Message)" $Colors.Red
    exit 1
}

# Enhanced function to load environment file with validation
=======
# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-ColorOutput "⚠️  Virtual environment not found. Creating..." $Colors.Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-ColorOutput "📦 Activating virtual environment..." $Colors.Green
& ".\.venv\Scripts\Activate.ps1"

# Function to load environment file
>>>>>>> 9039104 (Add missing project files and documentation)
function Import-EnvFile {
    param([string]$FilePath)
    
    if (Test-Path $FilePath) {
        Write-ColorOutput "📝 Loading environment variables from $FilePath" $Colors.Green
<<<<<<< HEAD
        $loadedCount = 0
        Get-Content $FilePath | ForEach-Object {
            if ($_ -match "^([^#][^=]*?)=(.*)$") {
                $name = $matches[1].Trim()
                # Remove quotes from value
                $value = $matches[2].Trim().Trim('"').Trim("'")
                
                # Validate variable name
                if ($name -match '^[A-Z_][A-Z0-9_]*$') {
                    [Environment]::SetEnvironmentVariable($name, $value, "Process")
                    $loadedCount++
                    if ($Verbose) {
                        Write-ColorOutput "   Set: $name" $Colors.DarkGray
                    }
                } else {
                    Write-ColorOutput "   ⚠️  Skipping invalid variable name: $name" $Colors.Yellow
                }
            }
        }
        Write-ColorOutput "   Loaded $loadedCount variables" $Colors.Cyan
    }
}

# Load environment variables from multiple sources with priority
Write-Section "🔧 Loading Environment Configuration"
@(".env", ".env.local", ".env.development", ".env.commercial") | ForEach-Object {
    Import-EnvFile $_
}

# Commercial lending specific environment setup
$env:COMMERCIAL_VIEW_ROOT = (Get-Location).Path
$env:COMMERCIAL_VIEW_MODE = if ($Production) { "production" } else { "development" }
$env:PRICING_CONFIG_PATH = "$($env:COMMERCIAL_VIEW_ROOT)\configs\pricing_config.yml"
$env:DPD_POLICY_PATH = "$($env:COMMERCIAL_VIEW_ROOT)\configs\dpd_policy.yml"
$env:COLUMN_MAPS_PATH = "$($env:COMMERCIAL_VIEW_ROOT)\configs\column_maps.yml"
$env:DATA_DIR = "$($env:COMMERCIAL_VIEW_ROOT)\data"
$env:EXPORT_DIR = "$($env:COMMERCIAL_VIEW_ROOT)\abaco_runtime\exports"

# Enhanced Python path setup
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$($env:COMMERCIAL_VIEW_ROOT)\src;$($env:COMMERCIAL_VIEW_ROOT)\scripts;$($env:PYTHONPATH)"
} else {
    $env:PYTHONPATH = "$($env:COMMERCIAL_VIEW_ROOT)\src;$($env:COMMERCIAL_VIEW_ROOT)\scripts"
}

# Set development/production environment variables
$env:ENVIRONMENT = if ($Production) { "production" } else { "development" }
$env:DEBUG = if ($Production) { "false" } else { "true" }
=======
        Get-Content $FilePath | ForEach-Object {
            if ($_ -match "^([^#][^=]*?)=(.*)$") {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
}

# Load environment variables from multiple sources
@(".env", ".env.local", ".env.development") | ForEach-Object {
    Import-EnvFile $_
}

# Load MCP server environment if exists
if (Test-Path ".env.mcp") {
    Write-ColorOutput "🔗 Loading MCP server configuration" $Colors.Green
    Import-EnvFile ".env.mcp"
}

# Set project-specific paths
$env:COMMERCIAL_VIEW_ROOT = (Get-Location).Path
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$($env:COMMERCIAL_VIEW_ROOT)\src;$($env:PYTHONPATH)"
} else {
    $env:PYTHONPATH = "$($env:COMMERCIAL_VIEW_ROOT)\src"
}

# Set development environment variables
$env:ENVIRONMENT = "development"
$env:DEBUG = "true"
>>>>>>> 9039104 (Add missing project files and documentation)
if (-not $env:API_BASE_URL) {
    $env:API_BASE_URL = "http://localhost:8000"
}

<<<<<<< HEAD
# Create required directories for commercial lending operations
Write-Section "📁 Setting Up Directory Structure"
$requiredDirectories = @(
    "var\log",
    "var\run",
    "data\pricing",
    "data\raw",
    "data\processed",
    "data\exports",
    "abaco_runtime\exports\kpi\json",
    "abaco_runtime\exports\kpi\csv",
    "abaco_runtime\exports\dpd",
    "abaco_runtime\exports\buckets",
    "abaco_runtime\exports\reports",
    "abaco_runtime\exports\regulatory",
    "certs",
    "backups",
    "temp",
    "notebooks\commercial_lending",
    "notebooks\risk_analysis",
    "reports\monthly",
    "reports\quarterly"
)

$createdDirs = 0
foreach ($dir in $requiredDirectories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-ColorOutput "📁 Created: $dir" $Colors.Cyan
        $createdDirs++
    }
}

if ($createdDirs -gt 0) {
    Write-ColorOutput "✅ Created $createdDirs directories" $Colors.Green
} else {
    Write-ColorOutput "✅ All required directories exist" $Colors.Green
}

# Display comprehensive status
Write-Section "🚀 Environment Status"
=======
# Display status
Write-ColorOutput "✅ Commercial-View development environment ready" $Colors.Green
>>>>>>> 9039104 (Add missing project files and documentation)
Write-ColorOutput "📁 Project root: $($env:COMMERCIAL_VIEW_ROOT)" $Colors.Blue
Write-ColorOutput "🐍 Python path: $($env:PYTHONPATH)" $Colors.Blue
Write-ColorOutput "💻 Virtual environment: $(Get-Command python | Select-Object -ExpandProperty Source)" $Colors.Blue
Write-ColorOutput "🌐 API Base URL: $($env:API_BASE_URL)" $Colors.Blue
<<<<<<< HEAD
Write-ColorOutput "💼 Commercial lending mode: $($env:COMMERCIAL_VIEW_MODE)" $Colors.Blue
Write-ColorOutput "📊 Data directory: $($env:DATA_DIR)" $Colors.Blue
Write-ColorOutput "📤 Export directory: $($env:EXPORT_DIR)" $Colors.Blue

# Enhanced Python version validation
$pythonVersion = & python --version
Write-ColorOutput "🐍 Python version: $pythonVersion" $Colors.Blue

# Check Python version compatibility
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-ColorOutput "❌ Python 3.8+ required, found $pythonVersion" $Colors.Red
        exit 1
    } else {
        Write-ColorOutput "✅ Python version compatible" $Colors.Green
    }
}

# Validate commercial lending configuration files
Write-Section "🔍 Configuration Validation"
$configFiles = @(
    $env:PRICING_CONFIG_PATH,
    $env:DPD_POLICY_PATH,
    $env:COLUMN_MAPS_PATH
)

$missingConfigs = @()
$validConfigs = 0

foreach ($config in $configFiles) {
    $fileName = Split-Path $config -Leaf
    if (Test-Path $config) {
        Write-ColorOutput "✅ Found: $fileName" $Colors.Green
        $validConfigs++
    } else {
        Write-ColorOutput "❌ Missing: $fileName" $Colors.Red
        $missingConfigs += $config
    }
}

if ($missingConfigs) {
    Write-ColorOutput "⚠️  Missing $($missingConfigs.Count) configuration files" $Colors.Yellow
    Write-ColorOutput "📋 Commercial lending features may be limited" $Colors.Yellow
} else {
    Write-ColorOutput "✅ All $validConfigs configuration files found" $Colors.Green
}

# Enhanced dependency checking with categorization
if (-not $SkipDependencyCheck) {
    Write-Section "📦 Dependency Validation"
    
    $coreDependencies = @("fastapi", "uvicorn", "pandas", "numpy", "pydantic", "yaml")
    $commercialDeps = @("requests", "scipy", "scikit-learn", "openpyxl")
    $devTools = @("pytest", "black", "mypy", "flake8")
    
    $missingCore = @()
    $missingCommercial = @()
    $missingDev = @()
    
    # Check core dependencies
    foreach ($dep in $coreDependencies) {
        if (Test-PythonModule $dep) {
            Write-ColorOutput "✅ $dep" $Colors.Green
        } else {
            Write-ColorOutput "❌ $dep (core)" $Colors.Red
            $missingCore += $dep
        }
    }
    
    # Check commercial lending dependencies
    foreach ($dep in $commercialDeps) {
        if (Test-PythonModule $dep) {
            Write-ColorOutput "✅ $dep" $Colors.Green
        } else {
            Write-ColorOutput "⚠️  $dep (commercial)" $Colors.Yellow
            $missingCommercial += $dep
        }
    }
    
    # Check development tools
    foreach ($tool in $devTools) {
        if (Test-PythonModule $tool) {
            Write-ColorOutput "✅ $tool" $Colors.Cyan
        } else {
            Write-ColorOutput "💡 $tool (dev)" $Colors.Cyan
            $missingDev += $tool
        }
    }
    
    # Handle missing dependencies
    if ($missingCore) {
        Write-ColorOutput "❌ Critical dependencies missing: $($missingCore -join ', ')" $Colors.Red
        
        if ($AutoInstall) {
            Write-ColorOutput "📦 Installing core dependencies..." $Colors.Green
            & pip install -r requirements.txt
        } else {
            $response = Read-Host "Install core dependencies now? (y/N)"
=======

# Check Python version
$pythonVersion = & python --version
Write-ColorOutput "🐍 Python version: $pythonVersion" $Colors.Blue

# Check dependencies unless skipped
if (-not $SkipDependencyCheck) {
    Write-ColorOutput "📦 Checking dependencies..." $Colors.Blue
    
    $dependencies = @("fastapi", "uvicorn", "pandas", "numpy", "requests")
    $missingDeps = @()
    
    foreach ($dep in $dependencies) {
        try {
            & python -c "import $dep" 2>$null
        } catch {
            $missingDeps += $dep
        }
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-ColorOutput "⚠️  Missing dependencies: $($missingDeps -join ', ')" $Colors.Yellow
        Write-ColorOutput "💡 Run: pip install -r requirements.txt" $Colors.Yellow
        
        if ($AutoInstall) {
            Write-ColorOutput "📦 Installing dependencies automatically..." $Colors.Green
            & pip install -r requirements.txt
        } else {
            $response = Read-Host "Install missing dependencies now? (y/N)"
>>>>>>> 9039104 (Add missing project files and documentation)
            if ($response -eq "y" -or $response -eq "Y") {
                Write-ColorOutput "📦 Installing dependencies..." $Colors.Green
                & pip install -r requirements.txt
            }
        }
    } else {
<<<<<<< HEAD
        Write-ColorOutput "✅ All core dependencies installed" $Colors.Green
    }
    
    if ($missingCommercial) {
        Write-ColorOutput "⚠️  Commercial lending libraries missing: $($missingCommercial -join ', ')" $Colors.Yellow
        if ($AutoInstall) {
            Write-ColorOutput "📦 Installing commercial dependencies..." $Colors.Green
            & pip install $missingCommercial
        }
    }
    
    if ($missingDev -and -not $Production) {
        Write-ColorOutput "💡 Development tools missing: $($missingDev -join ', ')" $Colors.Cyan
        Write-ColorOutput "   Install with: pip install $($missingDev -join ' ')" $Colors.Cyan
    }
}

# Enhanced service status checking
Write-Section "🔍 Service Status"
try {
    $response = Invoke-WebRequest -Uri "$($env:API_BASE_URL)/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput "✅ API server running at $($env:API_BASE_URL)" $Colors.Green
        
        # Try to get detailed status
        try {
            $healthData = $response.Content | ConvertFrom-Json
            if ($healthData.status) {
                Write-ColorOutput "   Status: $($healthData.status)" $Colors.Cyan
            }
        } catch {
            # Ignore JSON parsing errors
        }
    }
} catch {
    Write-ColorOutput "⚠️  API server not running at $($env:API_BASE_URL)" $Colors.Yellow
    Write-ColorOutput "💡 Start with: cvdev" $Colors.Cyan
}

# Test internet connectivity
try {
    $null = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet -WarningAction SilentlyContinue
    Write-ColorOutput "✅ Internet connectivity" $Colors.Green
} catch {
    Write-ColorOutput "⚠️  Limited internet connectivity" $Colors.Yellow
}

# Enhanced function definitions for commercial lending development
Write-Section "🔧 Setting Up Development Functions"

# Server management functions
function cvserver { & python scripts\uvicorn_manager.py @args }
function cvdev { & python scripts\uvicorn_manager.py dev }
function cvprod { & python scripts\uvicorn_manager.py prod }
function cvperf { & python scripts\uvicorn_manager.py perf }
function cvkill { & python scripts\uvicorn_manager.py kill }
function cvhealth { & python scripts\uvicorn_manager.py health }
function cvstatus { & python scripts\uvicorn_manager.py status }

# Legacy compatibility
function cvapi { & python server_control.py @args }

# Testing and quality assurance
function cvtest { 
    if ($args) { & pytest -v --tb=short @args } 
    else { & pytest -v --tb=short }
}
function cvtestcov { & pytest --cov=src --cov-report=html --cov-report=term @args }
function cvlint { 
    Write-ColorOutput "🎨 Formatting code..." $Colors.Blue
    & python -m black src\ scripts\
    Write-ColorOutput "🔍 Type checking..." $Colors.Blue
    & python -m mypy src\
}
function cvcheck { 
    & python -m flake8 src\ scripts\
    & python -m black --check src\ scripts\
}

# Commercial lending specific operations
function cvprice { & python -m commercial_view.pricing.calculator @args }
function cvdpd { & python -m commercial_view.dpd.analyzer @args }
function cvkpi { & python -m commercial_view.kpi.generator @args }
function cvrisk { & python -m commercial_view.risk.assessor @args }
function cvexport { & python -m commercial_view.export.manager @args }

# Enhanced commercial lending functions
function cvportfolio { & python -m commercial_view.portfolio.analyzer @args }
function cvreports { & python -m commercial_view.reports.generator @args }
function cvregulatory { & python -m commercial_view.regulatory.compliance @args }
function cvstress { & python -m commercial_view.stress.testing @args }

# Data management functions
function cvdata { & python scripts\data_manager.py @args }
function cvsync { & python scripts\sync_github.py @args }
function cvupload { & python scripts\upload_to_drive.py @args }
function cvbackup { & python scripts\backup_data.py @args }

# Configuration management
function cvconfig { & python scripts\config_validator.py @args }
function cvpricing { & python scripts\pricing_matrix_manager.py @args }

# Development utilities
function cvlog { 
    if (Test-Path "var\log\commercial_view.log") {
        Get-Content "var\log\commercial_view.log" -Wait -Tail 50
    } else {
        Write-ColorOutput "⚠️  Log file not found. Start server first." $Colors.Yellow
    }
}

function cvaccess { 
    if (Test-Path "var\log\access.log") {
        Get-Content "var\log\access.log" -Wait -Tail 50
    } else {
        Write-ColorOutput "⚠️  Access log not found." $Colors.Yellow
    }
}

function cvclean { 
    Write-ColorOutput "🧹 Cleaning Python cache files..." $Colors.Blue
    Get-ChildItem -Recurse -Force -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Force -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Force -Directory -Name ".pytest_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-ColorOutput "✅ Cache cleaned" $Colors.Green
}

function cvenv { Get-ChildItem Env: | Where-Object Name -like "COMMERCIAL_VIEW*" | Sort-Object Name }

# Enhanced Jupyter integration
function cvjupyter { 
    Write-ColorOutput "🔬 Starting Jupyter Lab for Commercial-View..." $Colors.Blue
    & python scripts\start_jupyter.py @args 
}

function cvnotebook { 
    param([string]$NotebookType = "analysis")
    $notebookDir = "notebooks\commercial_lending"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $notebookName = "${NotebookType}_${timestamp}.ipynb"
    $notebookPath = Join-Path $notebookDir $notebookName
    
    if (-not (Test-Path $notebookDir)) {
        New-Item -ItemType Directory -Path $notebookDir -Force | Out-Null
    }
    
    Write-ColorOutput "📓 Creating notebook: $notebookPath" $Colors.Green
    & jupyter lab $notebookPath
}

# Git shortcuts with enhanced functionality
function cvgit { 
    Write-ColorOutput "📊 Repository Status:" $Colors.Blue
    & git status --short
    Write-ColorOutput "`n📝 Recent Commits:" $Colors.Blue
    & git log --oneline --graph -10
}

function cvcommit {
    param([string]$Message)
    if (-not $Message) {
        Write-ColorOutput "Usage: cvcommit 'commit message'" $Colors.Yellow
        return
    }
    & git add .
    & git commit -m $Message
}

function cvpush { & git push origin main }
function cvpull { & git pull origin main }

# Enhanced help system
function cvhelp {
    Write-ColorOutput "🏦 Commercial-View Development Commands:" $Colors.Blue
    Write-ColorOutput ""
    Write-ColorOutput "Server Management:" $Colors.Cyan
    Write-ColorOutput "  cvdev       - Start development server"
    Write-ColorOutput "  cvprod      - Start production server"
    Write-ColorOutput "  cvperf      - Start high-performance server"
    Write-ColorOutput "  cvkill      - Stop server"
    Write-ColorOutput "  cvhealth    - Check server health"
    Write-ColorOutput "  cvstatus    - Show server status"
    Write-ColorOutput ""
    Write-ColorOutput "Commercial Lending Operations:" $Colors.Cyan
    Write-ColorOutput "  cvprice     - Commercial loan pricing"
    Write-ColorOutput "  cvdpd       - Days past due analysis"
    Write-ColorOutput "  cvkpi       - Generate KPI reports"
    Write-ColorOutput "  cvrisk      - Risk assessment"
    Write-ColorOutput "  cvexport    - Export management"
    Write-ColorOutput "  cvportfolio - Portfolio analysis"
    Write-ColorOutput "  cvreports   - Generate reports"
    Write-ColorOutput "  cvregulatory- Regulatory compliance"
    Write-ColorOutput "  cvstress    - Stress testing"
    Write-ColorOutput ""
    Write-ColorOutput "Development & Testing:" $Colors.Cyan
    Write-ColorOutput "  cvtest      - Run tests"
    Write-ColorOutput "  cvtestcov   - Run tests with coverage"
    Write-ColorOutput "  cvlint      - Format and type check"
    Write-ColorOutput "  cvcheck     - Check code quality"
    Write-ColorOutput ""
    Write-ColorOutput "Data & Configuration:" $Colors.Cyan
    Write-ColorOutput "  cvdata      - Data management"
    Write-ColorOutput "  cvconfig    - Configuration validation"
    Write-ColorOutput "  cvpricing   - Pricing matrix management"
    Write-ColorOutput ""
    Write-ColorOutput "Analysis & Notebooks:" $Colors.Cyan
    Write-ColorOutput "  cvjupyter   - Start Jupyter Lab"
    Write-ColorOutput "  cvnotebook  - Create new analysis notebook"
    Write-ColorOutput ""
    Write-ColorOutput "Utilities:" $Colors.Cyan
    Write-ColorOutput "  cvlog       - View application logs"
    Write-ColorOutput "  cvaccess    - View access logs"
    Write-ColorOutput "  cvclean     - Clean cache files"
    Write-ColorOutput "  cvenv       - Show environment variables"
    Write-ColorOutput ""
    Write-ColorOutput "Git Operations:" $Colors.Cyan
    Write-ColorOutput "  cvgit       - Repository status"
    Write-ColorOutput "  cvcommit    - Quick commit"
    Write-ColorOutput "  cvpush      - Push to main"
    Write-ColorOutput "  cvpull      - Pull from main"
    Write-ColorOutput ""
    Write-ColorOutput "📚 For detailed documentation, see: docs\" $Colors.Blue
}

# Display setup summary
Write-Section "✅ PowerShell Functions Configured"
Write-ColorOutput "   🖥️  Server: cvdev, cvprod, cvperf, cvkill, cvhealth, cvstatus"
Write-ColorOutput "   🧪 Testing: cvtest, cvtestcov, cvlint, cvcheck"
Write-ColorOutput "   💼 Commercial: cvprice, cvdpd, cvkpi, cvrisk, cvexport, cvportfolio"
Write-ColorOutput "   📊 Data: cvdata, cvconfig, cvpricing, cvbackup"
Write-ColorOutput "   📓 Analysis: cvjupyter, cvnotebook"
Write-ColorOutput "   🔧 Utils: cvlog, cvaccess, cvclean, cvenv"
Write-ColorOutput "   📝 Git: cvgit, cvcommit, cvpush, cvpull"

# Display quick start guide
Write-Section "🎯 Quick Start Guide"
Write-ColorOutput "   1. Start development server: " $Colors.White -NoNewline; Write-ColorOutput "cvdev" $Colors.Green
Write-ColorOutput "   2. Run tests: " $Colors.White -NoNewline; Write-ColorOutput "cvtest" $Colors.Green
Write-ColorOutput "   3. Check server health: " $Colors.White -NoNewline; Write-ColorOutput "cvhealth" $Colors.Green
Write-ColorOutput "   4. View logs: " $Colors.White -NoNewline; Write-ColorOutput "cvlog" $Colors.Green
Write-ColorOutput "   5. Generate KPIs: " $Colors.White -NoNewline; Write-ColorOutput "cvkpi" $Colors.Green
Write-ColorOutput "   6. Price commercial loans: " $Colors.White -NoNewline; Write-ColorOutput "cvprice" $Colors.Green
Write-ColorOutput "   7. Start Jupyter analysis: " $Colors.White -NoNewline; Write-ColorOutput "cvjupyter" $Colors.Green
Write-ColorOutput "   8. Get help: " $Colors.White -NoNewline; Write-ColorOutput "cvhelp" $Colors.Green

# Final status and recommendations
Write-Section "🎉 Setup Complete"
$totalIssues = $missingCore.Count + $missingConfigs.Count
$setupScore = [Math]::Max(0, 100 - ($totalIssues * 10))

if ($totalIssues -eq 0) {
    Write-ColorOutput "🎉 Commercial-View PowerShell environment fully configured! (Score: 100/100)" $Colors.Green
    Write-ColorOutput "🔗 API will be available at: $($env:API_BASE_URL)" $Colors.Green
    Write-ColorOutput "📚 Documentation: $($env:COMMERCIAL_VIEW_ROOT)\docs\" $Colors.Green
    Write-ColorOutput "💡 Ready for commercial lending operations!" $Colors.Green
} else {
    Write-ColorOutput "⚠️  Environment setup complete with $totalIssues warning(s) (Score: $setupScore/100)" $Colors.Yellow
    Write-ColorOutput "🔧 Resolve issues above to achieve 100% setup score" $Colors.Yellow
}

Write-ColorOutput ""
Write-ColorOutput "💡 Pro Tips for Commercial Lending Development:" $Colors.Cyan
Write-ColorOutput "   • Use " -NoNewline; Write-ColorOutput "cvhelp" $Colors.Green -NoNewline; Write-ColorOutput " for comprehensive command reference"
Write-ColorOutput "   • Use " -NoNewline; Write-ColorOutput "cvdev" $Colors.Green -NoNewline; Write-ColorOutput " to start development server with hot reload"
Write-ColorOutput "   • Use " -NoNewline; Write-ColorOutput "cvjupyter" $Colors.Green -NoNewline; Write-ColorOutput " for interactive data analysis"
Write-ColorOutput "   • Use " -NoNewline; Write-ColorOutput "cvlog" $Colors.Green -NoNewline; Write-ColorOutput " to monitor real-time application logs"
Write-ColorOutput "   • Use " -NoNewline; Write-ColorOutput "cvtest" $Colors.Green -NoNewline; Write-ColorOutput " before committing changes"

Write-ColorOutput "`n💻 Enhanced PowerShell environment ready for Commercial-View! 🚀💰" $Colors.Blue
=======
        Write-ColorOutput "✅ All core dependencies are installed" $Colors.Green
    }
    
    # Check for optional development tools
    $devTools = @("pytest", "black", "mypy")
    $missingDevTools = @()
    
    foreach ($tool in $devTools) {
        try {
            & python -c "import $tool" 2>$null
        } catch {
            $missingDevTools += $tool
        }
    }
    
    if ($missingDevTools.Count -gt 0) {
        Write-ColorOutput "💡 Optional dev tools missing: $($missingDevTools -join ', ')" $Colors.Yellow
        Write-ColorOutput "   Install with: pip install $($missingDevTools -join ' ')" $Colors.Yellow
    }
}

# Create data directory if it doesn't exist
if (-not (Test-Path "data")) {
    Write-ColorOutput "📁 Creating data directory..." $Colors.Yellow
    New-Item -ItemType Directory -Path "data" -Force | Out-Null
    New-Item -ItemType Directory -Path "data\raw" -Force | Out-Null
    New-Item -ItemType Directory -Path "data\processed" -Force | Out-Null
    New-Item -ItemType Directory -Path "data\exports" -Force | Out-Null
}

# Check if API server is running
Write-ColorOutput "🔍 Checking services..." $Colors.Blue
try {
    $response = Invoke-WebRequest -Uri "$($env:API_BASE_URL)/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-ColorOutput "✅ API server is running at $($env:API_BASE_URL)" $Colors.Green
    }
} catch {
    Write-ColorOutput "⚠️  API server not running at $($env:API_BASE_URL)" $Colors.Yellow
    Write-ColorOutput "💡 Start with: python server_control.py" $Colors.Yellow
}

# Create helpful functions
function cvapi { & python server_control.py @args }
function cvtest { & pytest -v @args }
function cvlint { 
    & python -m black src\ scripts\
    & python -m mypy src\
}
function cvsync { & python scripts\sync_github.py @args }
function cvupload { & python scripts\upload_to_drive.py @args }
function cvbuild { & python scripts\build.py @args }

# Display useful commands
Write-ColorOutput "`n📚 Useful Commands:" $Colors.Blue
Write-ColorOutput "  🚀 Start API server:      cvapi" $Colors.Cyan
Write-ColorOutput "  🧪 Run tests:             cvtest" $Colors.Cyan
Write-ColorOutput "  🎨 Format & lint code:    cvlint" $Colors.Cyan
Write-ColorOutput "  📤 Sync to GitHub:        cvsync" $Colors.Cyan
Write-ColorOutput "  ☁️  Upload to Drive:       cvupload" $Colors.Cyan
Write-ColorOutput "  🔧 Build project:         cvbuild" $Colors.Cyan

Write-ColorOutput "`n🎉 PowerShell environment setup complete! Happy coding! 🎉" $Colors.Green
>>>>>>> 9039104 (Add missing project files and documentation)
