#!/bin/bash
# Project-specific activation script for Commercial-View

set -e  # Exit on any error

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
