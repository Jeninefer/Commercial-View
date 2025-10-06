#!/bin/csh
# Project-specific activation script for Commercial-View (C shell version)

echo "🏦 Initializing Commercial-View Commercial Lending Platform..."

# Activate virtual environment
if ( -f ".venv/bin/activate.csh" ) then
    source .venv/bin/activate.csh
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
endif

# Load environment variables if .env exists
if ( -f ".env" ) then
    echo "📝 Loading environment variables from .env"
    source .env
endif

# Set project-specific paths
setenv COMMERCIAL_VIEW_ROOT "`pwd`"
if ( "$?PYTHONPATH" ) then
    setenv PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src:$COMMERCIAL_VIEW_ROOT/scripts:$PYTHONPATH"
else
    setenv PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src:$COMMERCIAL_VIEW_ROOT/scripts"
endif

# Commercial lending specific environment variables
setenv COMMERCIAL_VIEW_MODE "development"
setenv PRICING_CONFIG_PATH "$COMMERCIAL_VIEW_ROOT/configs/pricing_config.yml"
setenv DPD_POLICY_PATH "$COMMERCIAL_VIEW_ROOT/configs/dpd_policy.yml"
setenv COLUMN_MAPS_PATH "$COMMERCIAL_VIEW_ROOT/configs/column_maps.yml"
setenv DATA_DIR "$COMMERCIAL_VIEW_ROOT/data"
setenv EXPORT_DIR "$COMMERCIAL_VIEW_ROOT/abaco_runtime/exports"

# Set development environment variables
setenv ENVIRONMENT "development"
setenv DEBUG "true"
if ( ! "$?API_BASE_URL" ) then
    setenv API_BASE_URL "http://localhost:8000"
endif

# Ensure required directories exist
set required_dirs = ("var/log" "var/run" "data/pricing" "abaco_runtime/exports/kpi/json" "abaco_runtime/exports/kpi/csv" "abaco_runtime/exports/dpd" "abaco_runtime/exports/buckets")

foreach dir ($required_dirs)
    if ( ! -d "$dir" ) then
        mkdir -p "$dir"
        echo "📁 Created directory: $dir"
    endif
end

# Display comprehensive status
echo ""
echo "🚀 Commercial-View development environment ready (csh)"
echo "📁 Project root: $COMMERCIAL_VIEW_ROOT"
echo "🐍 Python path: $PYTHONPATH"
echo "💻 Virtual environment: `which python`"
echo "🌐 API Base URL: $API_BASE_URL"
echo "💼 Commercial lending mode: $COMMERCIAL_VIEW_MODE"
echo "📊 Data directory: $DATA_DIR"
echo "📤 Export directory: $EXPORT_DIR"

# Validate commercial lending configuration files
set config_files = ("$PRICING_CONFIG_PATH" "$DPD_POLICY_PATH" "$COLUMN_MAPS_PATH")
set missing_configs = ()

foreach config ($config_files)
    if ( ! -f "$config" ) then
        set missing_configs = ($missing_configs $config)
    endif
end

if ( $#missing_configs > 0 ) then
    echo "⚠️  Missing configuration files:"
    foreach config ($missing_configs)
        echo "   - $config"
    end
    echo "📋 Please ensure all configuration files are present before starting the server"
endif

# Check if required packages are installed
echo ""
echo "🔍 Checking dependencies..."

set required_packages = ("fastapi" "uvicorn" "pandas" "numpy" "pydantic" "yaml")
set missing_packages = ()

foreach package ($required_packages)
    python -c "import $package" >& /dev/null
    if ( $status != 0 ) then
        set missing_packages = ($missing_packages $package)
    endif
end

if ( $#missing_packages > 0 ) then
    echo "⚠️  Missing dependencies:"
    foreach package ($missing_packages)
        echo "   - $package"
    end
    echo "📦 Run: pip install -r requirements.txt"
else
    echo "✅ All required dependencies are installed"
endif

# Create comprehensive aliases for commercial lending development
echo ""
echo "🔧 Setting up development aliases..."

# Server management
alias cvserver "python scripts/uvicorn_manager.py"
alias cvdev "python scripts/uvicorn_manager.py dev"
alias cvprod "python scripts/uvicorn_manager.py prod"
alias cvperf "python scripts/uvicorn_manager.py perf"
alias cvkill "python scripts/uvicorn_manager.py kill"
alias cvhealth "python scripts/uvicorn_manager.py health"
alias cvstatus "python scripts/uvicorn_manager.py status"

# Legacy aliases for backward compatibility
alias cvapi "python server_control.py"

# Testing and quality assurance
alias cvtest "pytest -v --tb=short"
alias cvtestcov "pytest --cov=src --cov-report=html --cov-report=term"
alias cvlint "python -m black src/ scripts/ && python -m mypy src/"
alias cvcheck "python -m flake8 src/ scripts/ && python -m black --check src/ scripts/"

# Commercial lending specific operations
alias cvprice "python -m commercial_view.pricing.calculator"
alias cvdpd "python -m commercial_view.dpd.analyzer"  
alias cvkpi "python -m commercial_view.kpi.generator"
alias cvrisk "python -m commercial_view.risk.assessor"
alias cvexport "python -m commercial_view.export.manager"

# Data management
alias cvdata "python scripts/data_manager.py"
alias cvsync "python scripts/sync_github.py"
alias cvupload "python scripts/upload_to_drive.py"
alias cvbackup "python scripts/backup_data.py"

# Configuration management
alias cvconfig "python scripts/config_validator.py"
alias cvpricing "python scripts/pricing_matrix_manager.py"

# Development utilities
alias cvlog "tail -f var/log/commercial_view.log"
alias cvaccess "tail -f var/log/access.log"
alias cvclean "find . -name '*.pyc' -delete && find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"
alias cvenv "env | grep COMMERCIAL_VIEW"

# Git shortcuts for commercial lending development
alias cvgit "git status && echo '' && git log --oneline -5"
alias cvcommit "git add . && git commit -m"
alias cvpush "git push origin main"
alias cvpull "git pull origin main"

echo "✅ Development aliases configured:"
echo "   🖥️  Server: cvserver, cvdev, cvprod, cvperf, cvkill, cvhealth, cvstatus"
echo "   🧪 Testing: cvtest, cvtestcov, cvlint, cvcheck"
echo "   💼 Commercial: cvprice, cvdpd, cvkpi, cvrisk, cvexport"
echo "   📊 Data: cvdata, cvsync, cvupload, cvbackup"
echo "   ⚙️  Config: cvconfig, cvpricing"
echo "   🔧 Utils: cvlog, cvaccess, cvclean, cvenv"
echo "   📝 Git: cvgit, cvcommit, cvpush, cvpull"

# Display quick start guide
echo ""
echo "🎯 Quick Start Guide:"
echo "   1. Start development server: cvdev"
echo "   2. Run tests: cvtest"
echo "   3. Check server health: cvhealth"
echo "   4. View logs: cvlog"
echo "   5. Generate KPIs: cvkpi"
echo "   6. Price commercial loans: cvprice"

# Final status check
echo ""
if ( $#missing_packages == 0 && $#missing_configs == 0 ) then
    echo "🎉 Commercial-View development environment fully configured and ready!"
    echo "🔗 API will be available at: $API_BASE_URL"
    echo "📚 Documentation: $COMMERCIAL_VIEW_ROOT/docs/"
else
    echo "⚠️  Environment setup complete with warnings (see above)"
    echo "🔧 Please resolve missing dependencies and configurations"
endif

echo ""
echo "💡 Type 'cvdev' to start the development server"
echo "💡 Type 'cvhelp' for additional command information"

# Create help command
alias cvhelp 'echo "🏦 Commercial-View Development Commands:"; echo ""; echo "Server Management:"; echo "  cvdev      - Start development server"; echo "  cvprod     - Start production server"; echo "  cvperf     - Start high-performance server"; echo "  cvkill     - Stop server"; echo "  cvhealth   - Check server health"; echo "  cvstatus   - Show server status"; echo ""; echo "Commercial Lending:"; echo "  cvprice    - Commercial loan pricing"; echo "  cvdpd      - Days past due analysis"; echo "  cvkpi      - Generate KPI reports"; echo "  cvrisk     - Risk assessment"; echo "  cvexport   - Export management"; echo ""; echo "Development:"; echo "  cvtest     - Run tests"; echo "  cvlint     - Code formatting and linting"; echo "  cvlog      - View application logs"; echo "  cvclean    - Clean Python cache files"; echo ""; echo "For more help, see: docs/"'
