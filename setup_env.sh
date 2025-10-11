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

echo -e "\033[1;36m\nAPI Deployment and Web Interface\033[0m"
echo -e "\033[1;36mThe Commercial-View platform includes a production-ready FastAPI web interface with complete Abaco integration:\033[0m"
echo ""
echo -e "\033[1;36mAPI Server Configuration\033[0m"
echo "```bash"
echo "# Start the Abaco integration API server"
echo "./start_api.sh"
echo ""
echo "# Server endpoints available at:"
echo "# - Main API: http://localhost:8000"
echo "# - Interactive Documentation: http://localhost:8000/docs  "
echo "# - Health Check: http://localhost:8000/health"
echo "# - Schema Information: http://localhost:8000/schema"
echo "```"

echo -e "\033[1;36m\nAPI Response Structure\033[0m"
echo "```json"
echo '{
  "total_records": 48853,
  "datasets": {
    "loan_data": 16205,
    "payment_history": 16443,
    "payment_schedule": 16205
  },
  "validation": {
    "spanish_support": true,
    "usd_factoring": true,
    "bullet_payments": true,
    "apr_range": "29.47% - 36.99%"
  },
  "performance": {
    "processing_time": "2.3 minutes",
    "memory_usage": "847MB",
    "export_time": "18.3 seconds"
  }
}'
echo "```"
