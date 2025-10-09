#!/bin/bash
<<<<<<< HEAD
# Project-specific activation script for Commercial-View Commercial Lending Platform

set -e  # Exit on any error

# Enhanced color codes for comprehensive output
=======
# Project-specific activation script for Commercial-View

set -e  # Exit on any error

# Color codes for better output
>>>>>>> 9039104 (Add missing project files and documentation)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
<<<<<<< HEAD
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function for consistent colored output
print_color() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

print_section() {
    local title="$1"
    echo ""
    print_color "$BLUE" "$title"
    print_color "$BLUE" "$(printf '=%.0s' $(seq 1 ${#title}))"
}

print_color "$BLUE" "🏦 Initializing Commercial-View Commercial Lending Platform"
print_color "$BLUE" "$(printf '=%.0s' $(seq 1 60))"

# Enhanced directory validation
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    print_color "$RED" "❌ Error: Not in Commercial-View project root directory"
    print_color "$RED" "Please run this script from the project root directory"
    exit 1
fi

# Validate commercial lending project structure
required_paths=("configs" "src" "scripts" "docs")
missing_paths=()

for path in "${required_paths[@]}"; do
    if [ ! -d "$path" ]; then
        missing_paths+=("$path")
    fi
done

if [ ${#missing_paths[@]} -gt 0 ]; then
    print_color "$YELLOW" "⚠️  Missing project directories: ${missing_paths[*]}"
fi

# Enhanced virtual environment management
if [ ! -d ".venv" ]; then
    print_color "$YELLOW" "⚠️  Virtual environment not found. Creating..."
    if python3 -m venv .venv; then
        print_color "$GREEN" "✅ Virtual environment created successfully"
    else
        print_color "$RED" "❌ Failed to create virtual environment"
        exit 1
    fi
fi

print_color "$GREEN" "📦 Activating virtual environment..."
if source .venv/bin/activate; then
    print_color "$GREEN" "✅ Virtual environment activated successfully"
else
    print_color "$RED" "❌ Failed to activate virtual environment"
    exit 1
fi

# Enhanced environment variable loading with validation
print_section "🔧 Loading Environment Configuration"

load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        print_color "$GREEN" "📝 Loading environment variables from $env_file"
        local loaded_count=0
        
        # Validate file format
        if grep -q '^[^#]*=' "$env_file"; then
            set -a
            source "$env_file"
            set +a
            loaded_count=$(grep -c '^[^#]*=' "$env_file" || echo "0")
            print_color "$CYAN" "   Loaded $loaded_count variables"
        else
            print_color "$YELLOW" "   ⚠️  No valid variables found in $env_file"
        fi
    fi
}

# Load environment variables from multiple sources with priority
for env_file in ".env" ".env.local" ".env.development" ".env.commercial"; do
    load_env_file "$env_file"
done

# Commercial lending specific environment setup
export COMMERCIAL_VIEW_ROOT="$(pwd)"
export COMMERCIAL_VIEW_MODE="development"
export PRICING_CONFIG_PATH="$COMMERCIAL_VIEW_ROOT/configs/pricing_config.yml"
export DPD_POLICY_PATH="$COMMERCIAL_VIEW_ROOT/configs/dpd_policy.yml"
export COLUMN_MAPS_PATH="$COMMERCIAL_VIEW_ROOT/configs/column_maps.yml"
export DATA_DIR="$COMMERCIAL_VIEW_ROOT/data"
export EXPORT_DIR="$COMMERCIAL_VIEW_ROOT/abaco_runtime/exports"

# Enhanced Python path setup
if [ -n "$PYTHONPATH" ]; then
    export PYTHONPATH="$COMMERCIAL_VIEW_ROOT/src:$COMMERCIAL_VIEW_ROOT/scripts:$PYTHONPATH"
else
    export PYTHONPATH="$COMMERCIAL_VIEW_ROOT/src:$COMMERCIAL_VIEW_ROOT/scripts"
fi

# Set development environment variables with defaults
export ENVIRONMENT="development"
export DEBUG="true"
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
export API_VERSION="${API_VERSION:-v1}"

# Create required directories for commercial lending operations
print_section "📁 Setting Up Directory Structure"

required_directories=(
    "var/log"
    "var/run" 
    "var/cache"
    "data/pricing"
    "data/raw"
    "data/processed"
    "data/exports"
    "abaco_runtime/exports/kpi/json"
    "abaco_runtime/exports/kpi/csv"
    "abaco_runtime/exports/dpd"
    "abaco_runtime/exports/buckets"
    "abaco_runtime/exports/reports"
    "certs"
    "backups"
    "temp"
)

created_dirs=0
for dir in "${required_directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_color "$CYAN" "📁 Created directory: $dir"
        ((created_dirs++))
    fi
done

if [ $created_dirs -gt 0 ]; then
    print_color "$GREEN" "✅ Created $created_dirs directories"
else
    print_color "$GREEN" "✅ All required directories exist"
fi

# Display comprehensive status
print_section "🚀 Environment Status"
print_color "$BLUE" "📁 Project root: $COMMERCIAL_VIEW_ROOT"
print_color "$BLUE" "🐍 Python path: $PYTHONPATH"
print_color "$BLUE" "💻 Virtual environment: $(which python)"
print_color "$BLUE" "🌐 API Base URL: $API_BASE_URL"
print_color "$BLUE" "💼 Commercial lending mode: $COMMERCIAL_VIEW_MODE"
print_color "$BLUE" "📊 Data directory: $DATA_DIR"
print_color "$BLUE" "📤 Export directory: $EXPORT_DIR"

# Enhanced Python version validation
python_version=$(python --version 2>&1)
print_color "$BLUE" "🐍 Python version: $python_version"

# Check Python version compatibility
if python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    print_color "$GREEN" "✅ Python version compatible"
else
    print_color "$RED" "❌ Python 3.8+ required, found $python_version"
    exit 1
fi

# Validate commercial lending configuration files
print_section "🔍 Configuration Validation"

config_files=("$PRICING_CONFIG_PATH" "$DPD_POLICY_PATH" "$COLUMN_MAPS_PATH")
missing_configs=()
valid_configs=0

for config in "${config_files[@]}"; do
    filename=$(basename "$config")
    if [ -f "$config" ]; then
        print_color "$GREEN" "✅ Found: $filename"
        ((valid_configs++))
    else
        print_color "$RED" "❌ Missing: $filename"
        missing_configs+=("$config")
    fi
done

if [ ${#missing_configs[@]} -gt 0 ]; then
    print_color "$YELLOW" "⚠️  Missing ${#missing_configs[@]} configuration files"
    print_color "$YELLOW" "📋 Commercial lending features may be limited"
else
    print_color "$GREEN" "✅ All $valid_configs configuration files found"
fi

# Enhanced dependency checking with categorization
print_section "📦 Dependency Validation"

# Core dependencies for commercial lending
core_dependencies=("fastapi" "uvicorn" "pandas" "numpy" "pydantic" "yaml")
commercial_deps=("requests" "scipy" "scikit-learn" "openpyxl")
dev_tools=("pytest" "black" "mypy" "flake8")

missing_core=()
missing_commercial=()
missing_dev=()

# Check core dependencies
for dep in "${core_dependencies[@]}"; do
    if python -c "import $dep" 2>/dev/null; then
        print_color "$GREEN" "✅ $dep"
    else
        print_color "$RED" "❌ $dep (core)"
        missing_core+=("$dep")
    fi
done

# Check commercial lending dependencies
for dep in "${commercial_deps[@]}"; do
    if python -c "import $dep" 2>/dev/null; then
        print_color "$GREEN" "✅ $dep"
    else
        print_color "$YELLOW" "⚠️  $dep (commercial)"
        missing_commercial+=("$dep")
    fi
done

# Check development tools
for tool in "${dev_tools[@]}"; do
    if python -c "import $tool" 2>/dev/null; then
        print_color "$CYAN" "✅ $tool"
    else
        print_color "$CYAN" "💡 $tool (dev)"
        missing_dev+=("$tool")
    fi
done

# Handle missing dependencies
if [ ${#missing_core[@]} -gt 0 ]; then
    print_color "$RED" "❌ Critical dependencies missing: ${missing_core[*]}"
    print_color "$YELLOW" "📦 Installing core dependencies..."
    pip install -r requirements.txt
else
    print_color "$GREEN" "✅ All core dependencies installed"
fi

if [ ${#missing_commercial[@]} -gt 0 ]; then
    print_color "$YELLOW" "⚠️  Commercial lending libraries missing: ${missing_commercial[*]}"
    read -p "Install commercial lending dependencies? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_color "$GREEN" "📦 Installing commercial dependencies..."
        pip install "${missing_commercial[@]}"
    fi
fi

if [ ${#missing_dev[@]} -gt 0 ]; then
    print_color "$CYAN" "💡 Development tools missing: ${missing_dev[*]}"
fi

# Enhanced service status checking
print_section "🔍 Service Status"

# Check API server status
if curl -s "$API_BASE_URL/health" > /dev/null 2>&1; then
    print_color "$GREEN" "✅ API server running at $API_BASE_URL"
    
    # Try to get detailed status
    if server_status=$(curl -s "$API_BASE_URL/health" | python -c "import sys,json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null); then
        print_color "$CYAN" "   Status: $server_status"
    fi
else
    print_color "$YELLOW" "⚠️  API server not running at $API_BASE_URL"
    print_color "$CYAN" "💡 Use 'cvdev' to start the server"
fi

# Check internet connectivity
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    print_color "$GREEN" "✅ Internet connectivity"
else
    print_color "$YELLOW" "⚠️  Limited internet connectivity"
fi

# Enhanced function definitions for commercial lending development
print_section "🔧 Setting Up Development Functions"

# Server management functions
cvserver() { python scripts/uvicorn_manager.py "$@"; }
cvdev() { python scripts/uvicorn_manager.py dev; }
cvprod() { python scripts/uvicorn_manager.py prod; }
cvperf() { python scripts/uvicorn_manager.py perf; }
cvkill() { python scripts/uvicorn_manager.py kill; }
cvhealth() { python scripts/uvicorn_manager.py health; }
cvstatus() { python scripts/uvicorn_manager.py status; }

# Legacy compatibility
cvapi() { python server_control.py "$@"; }

# Testing and quality assurance
cvtest() { 
    if [ $# -eq 0 ]; then
        pytest -v --tb=short
    else
        pytest -v --tb=short "$@"
    fi
}
cvtestcov() { pytest --cov=src --cov-report=html --cov-report=term "$@"; }
cvlint() { 
    print_color "$BLUE" "🎨 Formatting code..."
    python -m black src/ scripts/
    print_color "$BLUE" "🔍 Type checking..."
    python -m mypy src/
}
cvcheck() { 
    python -m flake8 src/ scripts/
    python -m black --check src/ scripts/
}

# Commercial lending specific operations
cvprice() { python -m commercial_view.pricing.calculator "$@"; }
cvdpd() { python -m commercial_view.dpd.analyzer "$@"; }
cvkpi() { python -m commercial_view.kpi.generator "$@"; }
cvrisk() { python -m commercial_view.risk.assessor "$@"; }
cvexport() { python -m commercial_view.export.manager "$@"; }

# Data management functions
cvdata() { python scripts/data_manager.py "$@"; }
cvsync() { python scripts/sync_github.py "$@"; }
cvupload() { python scripts/upload_to_drive.py "$@"; }
cvbackup() { python scripts/backup_data.py "$@"; }

# Configuration management
cvconfig() { python scripts/config_validator.py "$@"; }
cvpricing() { python scripts/pricing_matrix_manager.py "$@"; }

# Development utilities
cvlog() { 
    if [ -f "var/log/commercial_view.log" ]; then
        tail -f var/log/commercial_view.log
    else
        print_color "$YELLOW" "⚠️  Log file not found. Start server first."
    fi
}

cvaccess() { 
    if [ -f "var/log/access.log" ]; then
        tail -f var/log/access.log
    else
        print_color "$YELLOW" "⚠️  Access log not found."
    fi
}

cvclean() { 
    print_color "$BLUE" "🧹 Cleaning Python cache files..."
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    print_color "$GREEN" "✅ Cache cleaned"
}

cvenv() { env | grep COMMERCIAL_VIEW | sort; }

# Git shortcuts with enhanced functionality
cvgit() { 
    print_color "$BLUE" "📊 Repository Status:"
    git status --short
    echo ""
    print_color "$BLUE" "📝 Recent Commits:"
    git log --oneline --graph -10
}

cvcommit() {
    if [ $# -eq 0 ]; then
        print_color "$YELLOW" "Usage: cvcommit 'commit message'"
        return 1
    fi
    git add .
    git commit -m "$1"
}

cvpush() { git push origin main; }
cvpull() { git pull origin main; }

# Performance monitoring function
cvperf_monitor() {
    print_color "$BLUE" "📊 System Performance Monitor"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "Memory Usage: $(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2}')"
    echo "Disk Usage: $(df -h | awk '$NF=="/"{printf "%s", $5}')"
    
    if [ -f "var/log/commercial_view.log" ]; then
        echo "Log Size: $(du -sh var/log/commercial_view.log | cut -f1)"
    fi
}

# Enhanced help system
cvhelp() {
    print_color "$BLUE" "🏦 Commercial-View Development Commands:"
    echo ""
    print_color "$CYAN" "Server Management:"
    echo "  cvdev       - Start development server"
    echo "  cvprod      - Start production server"
    echo "  cvperf      - Start high-performance server"
    echo "  cvkill      - Stop server"
    echo "  cvhealth    - Check server health"
    echo "  cvstatus    - Show server status"
    echo ""
    print_color "$CYAN" "Commercial Lending Operations:"
    echo "  cvprice     - Commercial loan pricing"
    echo "  cvdpd       - Days past due analysis"
    echo "  cvkpi       - Generate KPI reports"
    echo "  cvrisk      - Risk assessment"
    echo "  cvexport    - Export management"
    echo ""
    print_color "$CYAN" "Development & Testing:"
    echo "  cvtest      - Run tests"
    echo "  cvtestcov   - Run tests with coverage"
    echo "  cvlint      - Format and type check"
    echo "  cvcheck     - Check code quality"
    echo ""
    print_color "$CYAN" "Data & Configuration:"
    echo "  cvdata      - Data management"
    echo "  cvconfig    - Configuration validation"
    echo "  cvpricing   - Pricing matrix management"
    echo ""
    print_color "$CYAN" "Utilities:"
    echo "  cvlog       - View application logs"
    echo "  cvaccess    - View access logs"
    echo "  cvclean     - Clean cache files"
    echo "  cvenv       - Show environment variables"
    echo "  cvperf_monitor - System performance"
    echo ""
    print_color "$CYAN" "Git Operations:"
    echo "  cvgit       - Repository status"
    echo "  cvcommit    - Quick commit"
    echo "  cvpush      - Push to main"
    echo "  cvpull      - Pull from main"
    echo ""
    print_color "$BLUE" "📚 For detailed documentation, see: docs/"
}

# Display setup summary
print_section "✅ Bash Functions Configured"
echo "   🖥️  Server: cvdev, cvprod, cvperf, cvkill, cvhealth, cvstatus"
echo "   🧪 Testing: cvtest, cvtestcov, cvlint, cvcheck"
echo "   💼 Commercial: cvprice, cvdpd, cvkpi, cvrisk, cvexport"
echo "   📊 Data: cvdata, cvconfig, cvpricing, cvbackup"
echo "   🔧 Utils: cvlog, cvaccess, cvclean, cvenv, cvperf_monitor"
echo "   📝 Git: cvgit, cvcommit, cvpush, cvpull"

# Display quick start guide
print_section "🎯 Quick Start Guide"
echo -e "   1. Start development server: ${GREEN}cvdev${NC}"
echo -e "   2. Monitor performance: ${GREEN}cvperf_monitor${NC}"
echo -e "   3. Run tests: ${GREEN}cvtest${NC}"
echo -e "   4. Check server health: ${GREEN}cvhealth${NC}"
echo -e "   5. View logs: ${GREEN}cvlog${NC}"
echo -e "   6. Generate KPIs: ${GREEN}cvkpi${NC}"
echo -e "   7. Price commercial loans: ${GREEN}cvprice${NC}"
echo -e "   8. Get help: ${GREEN}cvhelp${NC}"

# Final status and recommendations
print_section "🎉 Setup Complete"
total_issues=$((${#missing_core[@]} + ${#missing_configs[@]}))
setup_score=$((100 - total_issues * 10))

if [ $total_issues -eq 0 ]; then
    print_color "$GREEN" "🎉 Commercial-View Bash environment fully configured! (Score: 100/100)"
    print_color "$GREEN" "🔗 API will be available at: $API_BASE_URL"
    print_color "$GREEN" "📚 Documentation: $COMMERCIAL_VIEW_ROOT/docs/"
    print_color "$GREEN" "💡 Ready for commercial lending operations!"
else
    print_color "$YELLOW" "⚠️  Environment setup complete with $total_issues warning(s) (Score: $setup_score/100)"
    print_color "$YELLOW" "🔧 Resolve issues above to achieve 100% setup score"
fi

echo ""
print_color "$CYAN" "💡 Pro Tips for Commercial Lending Development:"
echo -e "   • Use ${GREEN}cvhelp${NC} for comprehensive command reference"
echo -e "   • Use ${GREEN}cvdev${NC} to start development server with hot reload"
echo -e "   • Use ${GREEN}cvlog${NC} to monitor real-time application logs"
echo -e "   • Use ${GREEN}cvtest${NC} before committing changes"
echo -e "   • Use ${GREEN}cvperf_monitor${NC} to track system performance"

echo ""
print_color "$BLUE" "🚀 Enhanced Bash environment ready for Commercial-View! 🏦💰"
=======
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Initializing Commercial-View Development Environment${NC}"
echo "=" * 50

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    echo -e "${RED}❌ Error: Not in Commercial-View project root directory${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
fi

echo -e "${GREEN}📦 Activating virtual environment...${NC}"
source .venv/bin/activate

# Load environment variables from multiple sources
for env_file in ".env" ".env.local" ".env.development"; do
    if [ -f "$env_file" ]; then
        echo -e "${GREEN}📝 Loading environment variables from $env_file${NC}"
        set -a
        source "$env_file"
        set +a
    fi
done

# Load MCP server environment if exists
if [ -f ".env.mcp" ]; then
    echo -e "${GREEN}🔗 Loading MCP server configuration${NC}"
    set -a
    source ".env.mcp"
    set +a
fi

# Set project-specific paths
export COMMERCIAL_VIEW_ROOT="$(pwd)"
export PYTHONPATH="$COMMERCIAL_VIEW_ROOT/src:$PYTHONPATH"

# Set development environment variables
export ENVIRONMENT="development"
export DEBUG="true"
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Display status
echo -e "${GREEN}✅ Commercial-View development environment ready${NC}"
echo -e "${BLUE}📁 Project root:${NC} $COMMERCIAL_VIEW_ROOT"
echo -e "${BLUE}🐍 Python path:${NC} $PYTHONPATH"
echo -e "${BLUE}💻 Virtual environment:${NC} $(which python)"
echo -e "${BLUE}🌐 API Base URL:${NC} $API_BASE_URL"

# Check Python version
python_version=$(python --version 2>&1)
echo -e "${BLUE}🐍 Python version:${NC} $python_version"

# Check if required packages are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
missing_deps=()

# Core dependencies
dependencies=("fastapi" "uvicorn" "pandas" "numpy" "requests")

for dep in "${dependencies[@]}"; do
    if ! python -c "import $dep" 2>/dev/null; then
        missing_deps+=("$dep")
    fi
done

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing dependencies: ${missing_deps[*]}${NC}"
    echo -e "${YELLOW}💡 Run: pip install -r requirements.txt${NC}"
    
    # Offer to install automatically
    read -p "Install missing dependencies now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}📦 Installing dependencies...${NC}"
        pip install -r requirements.txt
    fi
else
    echo -e "${GREEN}✅ All core dependencies are installed${NC}"
fi

# Check for optional development tools
dev_tools=("pytest" "black" "mypy")
missing_dev_tools=()

for tool in "${dev_tools[@]}"; do
    if ! python -c "import $tool" 2>/dev/null; then
        missing_dev_tools+=("$tool")
    fi
done

if [ ${#missing_dev_tools[@]} -gt 0 ]; then
    echo -e "${YELLOW}💡 Optional dev tools missing: ${missing_dev_tools[*]}${NC}"
    echo -e "${YELLOW}   Install with: pip install ${missing_dev_tools[*]}${NC}"
fi

# Check for data directory
if [ ! -d "data" ]; then
    echo -e "${YELLOW}📁 Creating data directory...${NC}"
    mkdir -p data/{raw,processed,exports}
fi

# Check if services are running
echo -e "${BLUE}🔍 Checking services...${NC}"

# Check if API server is running
if curl -s "$API_BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API server is running at $API_BASE_URL${NC}"
else
    echo -e "${YELLOW}⚠️  API server not running at $API_BASE_URL${NC}"
    echo -e "${YELLOW}💡 Start with: python server_control.py${NC}"
fi

# Display useful commands
echo -e "\n${BLUE}📚 Useful Commands:${NC}"
echo "  🚀 Start API server:      python server_control.py"
echo "  🧪 Run tests:             pytest"
echo "  🎨 Format code:           python -m black src/ scripts/"
echo "  🔍 Type check:            python -m mypy src/"
echo "  📤 Sync to GitHub:        python scripts/sync_github.py"
echo "  ☁️  Upload to Drive:       python scripts/upload_to_drive.py"
echo "  🔗 Setup MCP servers:     python scripts/build.py mcp"

# Create helpful aliases
alias cvapi="python server_control.py"
alias cvtest="pytest -v"
alias cvlint="python -m black src/ scripts/ && python -m mypy src/"
alias cvsync="python scripts/sync_github.py"
alias cvupload="python scripts/upload_to_drive.py"

echo -e "\n${GREEN}🎉 Environment setup complete! Happy coding! 🎉${NC}"
>>>>>>> 9039104 (Add missing project files and documentation)
