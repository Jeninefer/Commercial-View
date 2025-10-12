#!/bin/bash

echo "🏦 Commercial-View Abaco Integration Test"
echo "========================================"

# Ensure we're in the project root
cd "$(dirname "$0")"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo "💡 Please run: source .venv/bin/activate"
    exit 1
fi

# Check if required directories exist
if [ ! -d "src" ] || [ ! -d "config" ]; then
    echo "❌ Not in project root directory"
    echo "💡 Please run from: /Users/jenineferderas/Documents/GitHub/Commercial-View"
    exit 1
fi

echo "✅ Running from correct directory: $(pwd)"
echo "✅ Virtual environment: $VIRTUAL_ENV"
echo ""

# Run the integration test
python scripts/complete_integration_test.py

echo ""
echo "🎯 Integration test complete!"
