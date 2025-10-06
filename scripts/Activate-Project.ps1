<#
.Synopsis
Activate Commercial-View development environment for PowerShell session.

.Description
Activates the Python virtual environment and sets up project-specific 
environment variables, paths, and development tools for Commercial-View.

.Parameter SkipDependencyCheck
Skip checking for required Python dependencies.

.Parameter AutoInstall
Automatically install missing dependencies without prompting.

.Example
.\scripts\Activate-Project.ps1
Activates the Commercial-View development environment.

.Example
.\scripts\Activate-Project.ps1 -AutoInstall
Activates the environment and automatically installs missing dependencies.
#>

[CmdletBinding()]
param(
    [switch]$SkipDependencyCheck,
    [switch]$AutoInstall
)

# Color definitions for output
$Colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "🚀 Initializing Commercial-View Development Environment" $Colors.Blue
Write-ColorOutput ("=" * 50) $Colors.Blue

# Check if we're in the correct directory
if (-not (Test-Path "requirements.txt") -or -not (Test-Path "src")) {
    Write-ColorOutput "❌ Error: Not in Commercial-View project root directory" $Colors.Red
    Write-ColorOutput "Please run this script from the project root directory" $Colors.Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-ColorOutput "⚠️  Virtual environment not found. Creating..." $Colors.Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-ColorOutput "📦 Activating virtual environment..." $Colors.Green
& ".\.venv\Scripts\Activate.ps1"

# Function to load environment file
function Import-EnvFile {
    param([string]$FilePath)
    
    if (Test-Path $FilePath) {
        Write-ColorOutput "📝 Loading environment variables from $FilePath" $Colors.Green
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
if (-not $env:API_BASE_URL) {
    $env:API_BASE_URL = "http://localhost:8000"
}

# Display status
Write-ColorOutput "✅ Commercial-View development environment ready" $Colors.Green
Write-ColorOutput "📁 Project root: $($env:COMMERCIAL_VIEW_ROOT)" $Colors.Blue
Write-ColorOutput "🐍 Python path: $($env:PYTHONPATH)" $Colors.Blue
Write-ColorOutput "💻 Virtual environment: $(Get-Command python | Select-Object -ExpandProperty Source)" $Colors.Blue
Write-ColorOutput "🌐 API Base URL: $($env:API_BASE_URL)" $Colors.Blue

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
            if ($response -eq "y" -or $response -eq "Y") {
                Write-ColorOutput "📦 Installing dependencies..." $Colors.Green
                & pip install -r requirements.txt
            }
        }
    } else {
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
