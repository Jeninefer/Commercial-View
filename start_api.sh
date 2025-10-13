#!/bin/bash
# Commercial-View API Startup Script

set -e  # Exit on any error

echo "🚀 Starting Commercial-View API..."
echo 'Portfolio: $208M+ Abaco dataset (48,853 records)'
echo "Features: Spanish client support, USD factoring validation"

# Safer package checking using pip list instead of import
if ! pip list | grep -q "uvicorn"; then
    echo "❌ uvicorn not found. Installing..."
    python -m pip install --upgrade "uvicorn[standard]" fastapi || { 
        echo "❌ Failed to install required packages. Exiting."; 
        exit 1; 
    }
    echo "✅ uvicorn and fastapi installed successfully"
else
    echo "✅ uvicorn is available"
fi

# Verify the main application file exists
if [ ! -f "run.py" ] && [ ! -f "main.py" ]; then
    echo "❌ No main application file (run.py or main.py) found. Exiting."
    exit 1
fi

# Determine which application file to use
APP_FILE="run:app"
if [ -f "main.py" ]; then
    APP_FILE="main:app"
fi

# Start the API server
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📊 Application: ${APP_FILE}"
uvicorn "${APP_FILE}" --reload --host 0.0.0.0 --port 8000
