#!/usr/bin/env fish
# Project-specific activation script for Commercial-View (Fish shell version)

# Color definitions
set -l RED '\033[0;31m'
set -l GREEN '\033[0;32m'
set -l YELLOW '\033[1;33m'
set -l BLUE '\033[0;34m'
set -l NC '\033[0m'

echo -e $BLUE"🚀 Initializing Commercial-View Development Environment"$NC
echo (string repeat -n 50 "=")

# Check if we're in the correct directory
if not test -f "requirements.txt"; or not test -d "src"
    echo -e $RED"❌ Error: Not in Commercial-View project root directory"$NC
    echo "Please run this script from the project root directory"
    exit 1
end

# Create virtual environment if it doesn't exist
if not test -d ".venv"
    echo -e $YELLOW"⚠️  Virtual environment not found. Creating..."$NC
    python3 -m venv .venv
end

# Activate virtual environment
echo -e $GREEN"📦 Activating virtual environment..."$NC
source .venv/bin/activate.fish

# Function to load environment files
function load_env_file
    set env_file $argv[1]
    if test -f $env_file
        echo -e $GREEN"📝 Loading environment variables from $env_file"$NC
        for line in (cat $env_file | grep -v '^#' | grep -v '^$')
            set var_name (string split -m 1 '=' $line)[1]
            set var_value (string split -m 1 '=' $line)[2]
            set -gx $var_name $var_value
        end
    end
end

# Load environment variables from multiple sources
load_env_file ".env"
load_env_file ".env.local"
load_env_file ".env.development"

# Load MCP server environment if exists
if test -f ".env.mcp"
    echo -e $GREEN"🔗 Loading MCP server configuration"$NC
    load_env_file ".env.mcp"
end

# Set project-specific paths
set -gx COMMERCIAL_VIEW_ROOT (pwd)
if set -q PYTHONPATH
    set -gx PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src:$PYTHONPATH"
else
    set -gx PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src"
end

# Set development environment variables
set -gx ENVIRONMENT "development"
set -gx DEBUG "true"
if not set -q API_BASE_URL
    set -gx API_BASE_URL "http://localhost:8000"
end

# Display status
echo -e $GREEN"✅ Commercial-View development environment ready"$NC
echo -e $BLUE"📁 Project root:"$NC" $COMMERCIAL_VIEW_ROOT"
echo -e $BLUE"🐍 Python path:"$NC" $PYTHONPATH"
echo -e $BLUE"💻 Virtual environment:"$NC" "(which python)
echo -e $BLUE"🌐 API Base URL:"$NC" $API_BASE_URL"

# Check Python version
set python_version (python --version)
echo -e $BLUE"🐍 Python version:"$NC" $python_version"

# Check dependencies
echo -e $BLUE"📦 Checking dependencies..."$NC
set dependencies "fastapi" "uvicorn" "pandas" "numpy" "requests"
set missing_deps

for dep in $dependencies
    if not python -c "import $dep" 2>/dev/null
        set missing_deps $missing_deps $dep
    end
end

if test (count $missing_deps) -gt 0
    echo -e $YELLOW"⚠️  Missing dependencies: $missing_deps"$NC
    echo -e $YELLOW"💡 Run: pip install -r requirements.txt"$NC
    
    # Offer to install automatically
    read -P "Install missing dependencies now? (y/N): " -l response
    if test "$response" = "y"; or test "$response" = "Y"
        echo -e $GREEN"📦 Installing dependencies..."$NC
        pip install -r requirements.txt
    end
else
    echo -e $GREEN"✅ All core dependencies are installed"$NC
end

# Check for optional development tools
set dev_tools "pytest" "black" "mypy"
set missing_dev_tools

for tool in $dev_tools
    if not python -c "import $tool" 2>/dev/null
        set missing_dev_tools $missing_dev_tools $tool
    end
end

if test (count $missing_dev_tools) -gt 0
    echo -e $YELLOW"💡 Optional dev tools missing: $missing_dev_tools"$NC
    echo -e $YELLOW"   Install with: pip install $missing_dev_tools"$NC
end

# Create data directory if it doesn't exist
if not test -d "data"
    echo -e $YELLOW"📁 Creating data directory..."$NC
    mkdir -p data/{raw,processed,exports}
end

# Check if API server is running
echo -e $BLUE"🔍 Checking services..."$NC
if curl -s "$API_BASE_URL/health" >/dev/null 2>&1
    echo -e $GREEN"✅ API server is running at $API_BASE_URL"$NC
else
    echo -e $YELLOW"⚠️  API server not running at $API_BASE_URL"$NC
    echo -e $YELLOW"💡 Start with: python server_control.py"$NC
end

# Create helpful functions and aliases
function cvapi
    python server_control.py $argv
end

function cvtest
    pytest -v $argv
end

function cvlint
    python -m black src/ scripts/; and python -m mypy src/
end

function cvsync
    python scripts/sync_github.py $argv
end

function cvupload
    python scripts/upload_to_drive.py $argv
end

function cvbuild
    python scripts/build.py $argv
end

# Display useful commands
echo -e "\n"$BLUE"📚 Useful Commands:"$NC
echo "  🚀 Start API server:      cvapi"
echo "  🧪 Run tests:             cvtest"
echo "  🎨 Format & lint code:    cvlint"
echo "  📤 Sync to GitHub:        cvsync"
echo "  ☁️  Upload to Drive:       cvupload"
echo "  🔧 Build project:         cvbuild"

echo -e "\n"$GREEN"🎉 Fish shell environment setup complete! Happy coding! 🎉"$NC
