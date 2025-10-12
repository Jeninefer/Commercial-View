#!/bin/bash
# Commercial-View API Startup Script

echo "🚀 Starting Commercial-View API..."
echo "Portfolio: $208M+ Abaco dataset (48,853 records)"
echo "Features: Spanish client support, USD factoring validation"

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "❌ uvicorn not found. Installing..."
    python -m pip install "uvicorn[standard]" || { echo "❌ Failed to install uvicorn. Exiting."; exit 1; }
fi

# Start the API server
echo "✅ Starting FastAPI server on http://localhost:8000"
uvicorn run:app --reload --host 0.0.0.0 --port 8000
