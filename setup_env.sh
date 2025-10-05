#!/bin/bash

# Change to project root directory (where this script is located)
cd "$(dirname "$0")"

echo -e "\033[1;36m┌──────────────────────────────────────┐\033[0m"
echo -e "\033[1;36m│ Commercial View Environment Setup    │\033[0m"
echo -e "\033[1;36m└──────────────────────────────────────┘\033[0m"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "\033[1;33mCreating virtual environment...\033[0m"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "\033[1;33mActivating virtual environment...\033[0m"
source .venv/bin/activate

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "\033[1;31mFailed to activate virtual environment!\033[0m"
    exit 1
fi

# Install requirements
echo -e "\033[1;33mInstalling Python dependencies...\033[0m"
pip install -r requirements.txt

# Verify installations
echo -e "\033[1;33mVerifying installations...\033[0m"
python -c "import pandas, numpy, pytest; print('✓ Core packages installed')"

echo -e "\033[1;32m✓ Environment setup complete!\033[0m"
echo -e "\033[1;32m✓ Virtual environment is now active\033[0m"
echo ""
echo -e "\033[1;36mUsage Instructions:\033[0m"
echo "- Run tests:    python -m pytest tests/"
echo "- Run API:      uvicorn run:app --reload"
echo "- Deactivate:   deactivate"
