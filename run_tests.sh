#!/bin/bash

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies if needed
echo "Reinstalling project dependencies..."
pip install -r requirements.txt

# Run the tests with proper Python environment
echo "Running tests..."
python -m pytest tests/test_api.py -v

# Show completion message
if [ $? -eq 0 ]; then
    echo -e "\n\033[92mTests completed successfully!\033[0m"
else
    echo -e "\n\033[91mTests failed.\033[0m"
fi

# Deactivate virtual environment when done
deactivate
