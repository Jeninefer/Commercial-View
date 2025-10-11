#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")"
echo -e "${BLUE}${BOLD}Navigated to:${NC} $(pwd)"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}${BOLD}Virtual environment not found!${NC}"
    echo -e "${YELLOW}Creating new virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if environment activated successfully
if [ "$VIRTUAL_ENV" = "" ]; then
    echo -e "${RED}${BOLD}Failed to activate virtual environment!${NC}"
    exit 1
fi

echo -e "${GREEN}${BOLD}✓ Virtual environment activated successfully${NC}"

# Check for required packages and install if needed
echo -e "${YELLOW}Checking required packages...${NC}"
python -c "import pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip install pandas numpy
fi

# Check for requirements.txt and install if exists
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
fi

echo -e "${GREEN}${BOLD}✓ Environment is ready!${NC}"

# Execute the requested Python file
if [ "$1" != "" ]; then
    echo -e "${BLUE}${BOLD}Running:${NC} python $1"
    python "$1"
else
    echo -e "${YELLOW}${BOLD}Available Python scripts:${NC}"
    find . -name "*.py" -not -path "*/\.*" | sort
    echo ""
    echo -e "${YELLOW}Run a script with:${NC} ./run_correctly.sh path/to/script.py"
fi
