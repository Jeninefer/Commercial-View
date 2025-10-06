#!/bin/bash

set -euo pipefail

# Change to project directory
cd "$(dirname "$0")"

VENV_DIR=".venv"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "Error: expected virtual environment activation script at $ACTIVATE_SCRIPT" >&2
    exit 1
fi

# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"
trap 'deactivate >/dev/null 2>&1' EXIT

python -m pip install --upgrade pip

# Reinstall dependencies if needed
echo "Installing project dependencies..."
python -m pip install -r requirements.txt

# Run the tests with proper Python environment
echo "Running tests..."
python -m pytest tests/test_api.py -v

echo -e "\n\033[92mTests completed successfully!\033[0m"
