#!/bin/bash

# Commercial-View Setup Script
# Automates the initial setup process

set -e  # Exit on error

echo "========================================"
echo "Commercial-View Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"
else
    echo -e "${RED}✗${NC} Python 3.11+ required. Found: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}!${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}✗${NC} requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating directory structure..."
mkdir -p data/pricing
mkdir -p outputs/reports
mkdir -p outputs/charts
mkdir -p outputs/models
mkdir -p outputs/data
mkdir -p logs
mkdir -p credentials
mkdir -p abaco_runtime/exports/kpi/json
mkdir -p abaco_runtime/exports/kpi/csv
mkdir -p abaco_runtime/exports/dpd
mkdir -p abaco_runtime/exports/buckets
echo -e "${GREEN}✓${NC} Directories created"

# Initialize package structure
echo ""
echo "Initializing Python package structure..."
touch src/__init__.py
touch src/utils/__init__.py
echo -e "${GREEN}✓${NC} Package structure initialized"

# Run tests to verify setup
echo ""
echo "Running tests..."
if command -v pytest &> /dev/null; then
    pytest -q || echo -e "${YELLOW}!${NC} Some tests failed (this is OK for initial setup)"
    echo -e "${GREEN}✓${NC} Test suite executed"
else
    echo -e "${YELLOW}!${NC} pytest not found, skipping tests"
fi

# Final instructions
echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Configure your data paths in config/column_maps.yml"
echo ""
echo "3. Start the API server:"
echo "   python run.py"
echo ""
echo "4. Or run the portfolio processing:"
echo "   python portfolio.py --config config/"
echo ""
echo "5. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "For more information, see QUICKSTART.md"
echo ""
