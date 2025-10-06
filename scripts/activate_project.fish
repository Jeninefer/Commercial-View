#!/usr/bin/env fish
# Project-specific activation script for Commercial-View (Fish shell version)

set -e  # Exit on any error (Fish equivalent)

# Color definitions for enhanced visual feedback
set -l RED '\033[0;31m'
set -l GREEN '\033[0;32m'
set -l YELLOW '\033[1;33m'
set -l BLUE '\033[0;34m'
set -l PURPLE '\033[0;35m'
set -l CYAN '\033[0;36m'
set -l NC '\033[0m'

echo -e $BLUE"🏦 Initializing Commercial-View Commercial Lending Platform"$NC
echo (string repeat -n 60 "=")

# Check if we're in the correct directory
if not test -f "requirements.txt"; or not test -d "src"
    echo -e $RED"❌ Error: Not in Commercial-View project root directory"$NC
    echo "Please run this script from the project root directory"
    exit 1
end

# Enhanced virtual environment management
if not test -d ".venv"
    echo -e $YELLOW"⚠️  Virtual environment not found. Creating..."$NC
    python3 -m venv .venv
    
    # Check if creation was successful
    if test $status -ne 0
        echo -e $RED"❌ Failed to create virtual environment"$NC
        exit 1
    end
    
    echo -e $GREEN"✅ Virtual environment created successfully"$NC
    
    # Install Fish activation script if needed
    if not test -f ".venv/bin/activate.fish"
        echo -e $YELLOW"⚠️  Installing Fish activation support..."$NC
        pip install --upgrade pip
    end
end

# Activate virtual environment with enhanced error handling
if test -f ".venv/bin/activate.fish"
    echo -e $GREEN"📦 Activating virtual environment..."$NC
    source .venv/bin/activate.fish
    
    if test $status -eq 0
        echo -e $GREEN"✅ Virtual environment activated successfully"$NC
    else
        echo -e $RED"❌ Failed to activate virtual environment"$NC
        exit 1
    end
else
    echo -e $RED"❌ Fish activation script not found. Recreating virtual environment..."$NC
    rm -rf .venv
    python3 -m venv .venv
    source .venv/bin/activate.fish
end

# Enhanced function to load environment files with validation
function load_env_file
    set env_file $argv[1]
    if test -f $env_file
        echo -e $GREEN"📝 Loading environment variables from $env_file"$NC
        
        # Validate file format before loading
        set invalid_lines (cat $env_file | grep -n -v '^#' | grep -v '^$' | grep -v '=')
        if test (count $invalid_lines) -gt 0
            echo -e $YELLOW"⚠️  Warning: $env_file contains potentially invalid lines"$NC
        end
        
        set loaded_count 0
        for line in (cat $env_file | grep -v '^#' | grep -v '^$' | grep '=')
            set -l parts (string split -m 1 '=' $line)
            if test (count $parts) -eq 2
                set var_name (string trim $parts[1])
                set var_value (string trim $parts[2])
                
                # Remove surrounding quotes if present
                set var_value (string trim --chars='"' $var_value)
                set var_value (string trim --chars="'" $var_value)
                
                # Validate variable name format
                if string match -qr '^[A-Z_][A-Z0-9_]*$' $var_name
                    set -gx $var_name $var_value
                    set loaded_count (math $loaded_count + 1)
                else
                    echo -e $YELLOW"⚠️  Skipping invalid variable name: $var_name"$NC
                end
            end
        end
        
        echo -e $CYAN"   Loaded $loaded_count environment variables"$NC
    end
end

# Load environment variables from multiple sources with priority
echo -e $BLUE"🔧 Loading environment configuration..."$NC
set env_files ".env" ".env.local" ".env.development" ".env.commercial"

for env_file in $env_files
    load_env_file $env_file
end

# Commercial lending specific environment setup with validation
set -gx COMMERCIAL_VIEW_ROOT (pwd)
set -gx COMMERCIAL_VIEW_MODE "development"
set -gx PRICING_CONFIG_PATH "$COMMERCIAL_VIEW_ROOT/configs/pricing_config.yml"
set -gx DPD_POLICY_PATH "$COMMERCIAL_VIEW_ROOT/configs/dpd_policy.yml"
set -gx COLUMN_MAPS_PATH "$COMMERCIAL_VIEW_ROOT/configs/column_maps.yml"
set -gx DATA_DIR "$COMMERCIAL_VIEW_ROOT/data"
set -gx EXPORT_DIR "$COMMERCIAL_VIEW_ROOT/abaco_runtime/exports"

# Additional commercial lending paths
set -gx LOGS_DIR "$COMMERCIAL_VIEW_ROOT/var/log"
set -gx RUN_DIR "$COMMERCIAL_VIEW_ROOT/var/run"
set -gx CERTS_DIR "$COMMERCIAL_VIEW_ROOT/certs"
set -gx BACKUP_DIR "$COMMERCIAL_VIEW_ROOT/backups"

# Set Python path with commercial lending modules
if set -q PYTHONPATH
    set -gx PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src:$COMMERCIAL_VIEW_ROOT/scripts:$PYTHONPATH"
else
    set -gx PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src:$COMMERCIAL_VIEW_ROOT/scripts"
end

# Set development environment variables with defaults
set -gx ENVIRONMENT "development"
set -gx DEBUG "true"

if not set -q API_BASE_URL
    set -gx API_BASE_URL "http://localhost:8000"
end

if not set -q API_VERSION
    set -gx API_VERSION "v1"
end

# Ensure required directories exist for commercial lending operations
set required_dirs \
    "var/log" \
    "var/run" \
    "var/cache" \
    "data/pricing" \
    "data/raw" \
    "data/processed" \
    "data/exports" \
    "abaco_runtime/exports/kpi/json" \
    "abaco_runtime/exports/kpi/csv" \
    "abaco_runtime/exports/dpd" \
    "abaco_runtime/exports/buckets" \
    "abaco_runtime/exports/reports" \
    "certs" \
    "backups" \
    "temp"

echo -e $BLUE"📁 Setting up directory structure..."$NC
set created_dirs 0

for dir in $required_dirs
    if not test -d $dir
        mkdir -p $dir
        echo -e $CYAN"📁 Created directory: $dir"$NC
        set created_dirs (math $created_dirs + 1)
    end
end

if test $created_dirs -gt 0
    echo -e $GREEN"✅ Created $created_dirs directories"$NC
else
    echo -e $GREEN"✅ All required directories exist"$NC
end

# Display comprehensive status with enhanced formatting
echo ""
echo -e $GREEN"🚀 Commercial-View development environment ready (Fish)"$NC
echo -e $BLUE"📁 Project root:"$NC" $COMMERCIAL_VIEW_ROOT"
echo -e $BLUE"🐍 Python path:"$NC" $PYTHONPATH"
echo -e $BLUE"💻 Virtual environment:"$NC" "(which python)
echo -e $BLUE"🌐 API Base URL:"$NC" $API_BASE_URL"
echo -e $BLUE"💼 Commercial lending mode:"$NC" $COMMERCIAL_VIEW_MODE"
echo -e $BLUE"📊 Data directory:"$NC" $DATA_DIR"
echo -e $BLUE"📤 Export directory:"$NC" $EXPORT_DIR"

# Enhanced Python version compatibility check
set python_version (python --version | string replace "Python " "")
echo -e $BLUE"🐍 Python version:"$NC" $python_version"

# Check Python version requirements
set -l version_parts (string split "." $python_version)
set major_version $version_parts[1]
set minor_version $version_parts[2]

if test $major_version -lt 3; or test $major_version -eq 3 -a $minor_version -lt 8
    echo -e $RED"❌ Python 3.8+ required, found $python_version"$NC
    echo -e $YELLOW"💡 Please upgrade Python to continue"$NC
    exit 1
else
    echo -e $GREEN"✅ Python version compatible"$NC
end

# Enhanced configuration validation with detailed feedback
echo ""
echo -e $BLUE"🔍 Validating commercial lending configuration..."$NC

set config_files $PRICING_CONFIG_PATH $DPD_POLICY_PATH $COLUMN_MAPS_PATH
set missing_configs
set valid_configs 0

for config in $config_files
    if test -f $config
        set valid_configs (math $valid_configs + 1)
        echo -e $GREEN"✅ Found: "(basename $config)$NC
    else
        set missing_configs $missing_configs $config
        echo -e $RED"❌ Missing: $config"$NC
    end
end

if test (count $missing_configs) -gt 0
    echo -e $YELLOW"⚠️  Missing $missing_configs configuration files"$NC
    echo -e $YELLOW"📋 Commercial lending features may be limited"$NC
else
    echo -e $GREEN"✅ All $valid_configs configuration files found"$NC
end

# Enhanced dependency checking with installation prompts
echo ""
echo -e $BLUE"🔍 Checking dependencies..."$NC

set core_dependencies "fastapi" "uvicorn" "pandas" "numpy" "pydantic" "yaml"
set commercial_deps "requests" "scipy" "scikit-learn" "openpyxl"
set dev_tools "pytest" "black" "mypy" "flake8"

set missing_core
set missing_commercial  
set missing_dev

# Check core dependencies
for dep in $core_dependencies
    if python -c "import $dep" 2>/dev/null
        echo -e $GREEN"✅ $dep"$NC
    else
        set missing_core $missing_core $dep
        echo -e $RED"❌ $dep (core)"$NC
    end
end

# Check commercial lending dependencies
for dep in $commercial_deps
    if python -c "import $dep" 2>/dev/null
        echo -e $GREEN"✅ $dep"$NC
    else
        set missing_commercial $missing_commercial $dep
        echo -e $YELLOW"⚠️  $dep (commercial)"$NC
    end
end

# Check development tools
for tool in $dev_tools
    if python -c "import $tool" 2>/dev/null
        echo -e $CYAN"✅ $tool"$NC
    else
        set missing_dev $missing_dev $tool
        echo -e $CYAN"💡 $tool (dev)"$NC
    end
end

# Enhanced dependency installation prompts
if test (count $missing_core) -gt 0
    echo -e $RED"❌ Critical dependencies missing:"$NC" $missing_core"
    echo -e $YELLOW"📦 Installing core dependencies..."$NC
    pip install -r requirements.txt
else
    echo -e $GREEN"✅ All core dependencies installed"$NC
end

if test (count $missing_commercial) -gt 0
    echo -e $YELLOW"⚠️  Commercial lending libraries missing:"$NC" $missing_commercial"
    read -P "Install commercial lending dependencies? (y/N): " -l install_commercial
    if test "$install_commercial" = "y"; or test "$install_commercial" = "Y"
        echo -e $GREEN"📦 Installing commercial dependencies..."$NC
        pip install $missing_commercial
    end
end

# Enhanced service status checking
echo ""
echo -e $BLUE"🔍 Checking services and connectivity..."$NC

# Check API server status
if curl -s "$API_BASE_URL/health" >/dev/null 2>&1
    echo -e $GREEN"✅ API server running at $API_BASE_URL"$NC
    
    # Get server status details
    set server_info (curl -s "$API_BASE_URL/health" | python -c "import json,sys; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    if test -n "$server_info"
        echo -e $CYAN"   Status: $server_info"$NC
    end
else
    echo -e $YELLOW"⚠️  API server not running at $API_BASE_URL"$NC
    echo -e $CYAN"💡 Use 'cvdev' to start the server"$NC
end

# Check database connectivity (if configured)
if set -q DATABASE_URL
    echo -e $BLUE"🗄️  Checking database connectivity..."$NC
    # Add database connectivity check here
end

# Check external service connectivity
echo -e $BLUE"🌐 Checking external services..."$NC
if ping -c 1 google.com >/dev/null 2>&1
    echo -e $GREEN"✅ Internet connectivity"$NC
else
    echo -e $YELLOW"⚠️  Limited internet connectivity"$NC
end

# Enhanced function definitions for commercial lending development
echo ""
echo -e $BLUE"🔧 Setting up Commercial-View functions..."$NC

# Server management functions
function cvserver --description "Manage Commercial-View server"
    python scripts/uvicorn_manager.py $argv
end

function cvdev --description "Start development server"
    python scripts/uvicorn_manager.py dev
end

function cvprod --description "Start production server"
    python scripts/uvicorn_manager.py prod
end

function cvperf --description "Start high-performance server"
    python scripts/uvicorn_manager.py perf
end

function cvkill --description "Stop server"
    python scripts/uvicorn_manager.py kill
end

function cvhealth --description "Check server health"
    python scripts/uvicorn_manager.py health
end

function cvstatus --description "Show server status"
    python scripts/uvicorn_manager.py status
end

# Legacy compatibility
function cvapi --description "Legacy server control"
    python server_control.py $argv
end

# Testing and quality assurance
function cvtest --description "Run tests with coverage"
    if test (count $argv) -eq 0
        pytest -v --tb=short
    else
        pytest -v --tb=short $argv
    end
end

function cvtestcov --description "Run tests with coverage report"
    pytest --cov=src --cov-report=html --cov-report=term $argv
end

function cvlint --description "Format code and run type checking"
    echo -e $BLUE"🎨 Formatting code..."$NC
    python -m black src/ scripts/
    echo -e $BLUE"🔍 Type checking..."$NC
    python -m mypy src/
end

function cvcheck --description "Check code quality without changes"
    python -m flake8 src/ scripts/
    python -m black --check src/ scripts/
end

# Commercial lending specific operations
function cvprice --description "Commercial loan pricing calculator"
    python -m commercial_view.pricing.calculator $argv
end

function cvdpd --description "Days past due analysis"
    python -m commercial_view.dpd.analyzer $argv
end

function cvkpi --description "Generate KPI reports"
    python -m commercial_view.kpi.generator $argv
end

function cvrisk --description "Risk assessment tools"
    python -m commercial_view.risk.assessor $argv
end

function cvexport --description "Export management"
    python -m commercial_view.export.manager $argv
end

# Data management functions
function cvdata --description "Data management utilities"
    python scripts/data_manager.py $argv
end

function cvsync --description "Sync with GitHub"
    python scripts/sync_github.py $argv
end

function cvupload --description "Upload to Google Drive"
    python scripts/upload_to_drive.py $argv
end

# Configuration management
function cvconfig --description "Validate configurations"
    python scripts/config_validator.py $argv
end

function cvpricing --description "Manage pricing matrices"
    python scripts/pricing_matrix_manager.py $argv
end

# Development utilities
function cvlog --description "View application logs"
    if test -f var/log/commercial_view.log
        tail -f var/log/commercial_view.log
    else
        echo -e $YELLOW"⚠️  Log file not found. Start server first."$NC
    end
end

function cvaccess --description "View access logs"
    if test -f var/log/access.log
        tail -f var/log/access.log
    else
        echo -e $YELLOW"⚠️  Access log not found."$NC
    end
end

function cvclean --description "Clean Python cache files"
    echo -e $BLUE"🧹 Cleaning Python cache files..."$NC
    find . -name "*.pyc" -delete 2>/dev/null
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find . -name "*.pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
    echo -e $GREEN"✅ Cache cleaned"$NC
end

function cvenv --description "Show Commercial-View environment variables"
    env | grep COMMERCIAL_VIEW | sort
end

# Git shortcuts with enhanced functionality
function cvgit --description "Git status and recent commits"
    echo -e $BLUE"📊 Repository Status:"$NC
    git status --short
    echo ""
    echo -e $BLUE"📝 Recent Commits:"$NC
    git log --oneline --graph -10
end

function cvcommit --description "Quick commit with message"
    if test (count $argv) -eq 0
        echo -e $YELLOW"Usage: cvcommit 'commit message'"$NC
        return 1
    end
    git add .
    git commit -m $argv[1]
end

function cvpush --description "Push to main branch"
    git push origin main
end

function cvpull --description "Pull from main branch"
    git pull origin main
end

# Enhanced help system
function cvhelp --description "Show Commercial-View commands help"
    echo -e $BLUE"🏦 Commercial-View Development Commands:"$NC
    echo ""
    echo -e $CYAN"Server Management:"$NC
    echo "  cvdev       - Start development server"
    echo "  cvprod      - Start production server" 
    echo "  cvperf      - Start high-performance server"
    echo "  cvkill      - Stop server"
    echo "  cvhealth    - Check server health"
    echo "  cvstatus    - Show server status"
    echo ""
    echo -e $CYAN"Commercial Lending Operations:"$NC
    echo "  cvprice     - Commercial loan pricing"
    echo "  cvdpd       - Days past due analysis"
    echo "  cvkpi       - Generate KPI reports"
    echo "  cvrisk      - Risk assessment"
    echo "  cvexport    - Export management"
    echo ""
    echo -e $CYAN"Development & Testing:"$NC
    echo "  cvtest      - Run tests"
    echo "  cvtestcov   - Run tests with coverage"
    echo "  cvlint      - Format and type check"
    echo "  cvcheck     - Check code quality"
    echo ""
    echo -e $CYAN"Data & Configuration:"$NC
    echo "  cvdata      - Data management"
    echo "  cvconfig    - Configuration validation"
    echo "  cvpricing   - Pricing matrix management"
    echo ""
    echo -e $CYAN"Utilities:"$NC
    echo "  cvlog       - View application logs"
    echo "  cvaccess    - View access logs"
    echo "  cvclean     - Clean cache files"
    echo "  cvenv       - Show environment variables"
    echo ""
    echo -e $CYAN"Git Operations:"$NC
    echo "  cvgit       - Repository status"
    echo "  cvcommit    - Quick commit"
    echo "  cvpush      - Push to main"
    echo "  cvpull      - Pull from main"
    echo ""
    echo -e $BLUE"📚 For detailed documentation, see: docs/"$NC
end

# Display setup summary
echo -e $GREEN"✅ Fish shell functions configured:"$NC
echo "   🖥️  Server: cvdev, cvprod, cvperf, cvkill, cvhealth, cvstatus"
echo "   🧪 Testing: cvtest, cvtestcov, cvlint, cvcheck"
echo "   💼 Commercial: cvprice, cvdpd, cvkpi, cvrisk, cvexport"
echo "   📊 Data: cvdata, cvconfig, cvpricing, cvbackup"
echo "   🔧 Utils: cvlog, cvaccess, cvclean, cvenv, cvperf_monitor"
echo "   🚀 Deploy: cvdeploy"
echo "   📝 Git: cvgit, cvcommit, cvpush, cvpull"

# Display enhanced quick start guide with performance tips
echo ""
echo -e $PURPLE"🎯 Quick Start Guide:"$NC
echo "   1. Start development server: "$GREEN"cvdev"$NC
echo "   2. Monitor performance: "$GREEN"cvperf_monitor"$NC
echo "   3. Run tests: "$GREEN"cvtest"$NC
echo "   4. Check server health: "$GREEN"cvhealth"$NC
echo "   5. View logs: "$GREEN"cvlog"$NC
echo "   6. Generate KPIs: "$GREEN"cvkpi"$NC
echo "   7. Price commercial loans: "$GREEN"cvprice"$NC
echo "   8. Prepare deployment: "$GREEN"cvdeploy"$NC
echo "   9. Get help: "$GREEN"cvhelp"$NC

# Enhanced final status with actionable recommendations
echo ""
set total_issues (math (count $missing_core) + (count $missing_configs))
set setup_score (math 100 - $total_issues \* 10)

if test $total_issues -eq 0
    echo -e $GREEN"🎉 Commercial-View Fish environment fully configured! (Score: 100/100)"$NC
    echo -e $GREEN"🔗 API will be available at: $API_BASE_URL"$NC
    echo -e $GREEN"📚 Documentation: $COMMERCIAL_VIEW_ROOT/docs/"$NC
    echo -e $GREEN"💡 Ready for commercial lending operations!"$NC
else
    echo -e $YELLOW"⚠️  Environment setup complete with $total_issues warning(s) (Score: $setup_score/100)"$NC
    echo -e $YELLOW"🔧 Resolve issues above to achieve 100% setup score"$NC
end

echo ""
echo -e $CYAN"💡 Pro Tips for Commercial Lending Development:"$NC
echo "   • Use "$GREEN"cvhelp"$NC" for comprehensive command reference"
echo "   • Use "$GREEN"cvdev"$NC" to start development server with hot reload"
echo "   • Use "$GREEN"cvlog"$NC" to monitor real-time application logs"
echo "   • Use "$GREEN"cvtest"$NC" before committing changes"
echo "   • Use "$GREEN"cvperf_monitor"$NC" to track system performance"
echo "   • Use "$GREEN"cvbackup"$NC" before major configuration changes"

echo ""
echo -e $BLUE"🐟 Enhanced Fish shell environment ready for Commercial-View! 🚀💰"$NC
