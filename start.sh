#!/bin/bash

# Commercial View - System Startup Script
echo "🚀 Starting Commercial View Analytics Platform..."

# Check if virtual environment exists, if not create it
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if needed
echo "📋 Installing/updating dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Create necessary directories
mkdir -p abaco_runtime/exports/{dpd,kpi/json,pricing,analytics}

# Start the application
echo "✅ Environment ready. Starting application..."
echo "🌐 API will be available at: http://localhost:8000"
echo "📊 Dashboard at: http://localhost:8000/docs"
echo ""

# Start the server
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
