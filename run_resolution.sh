#!/bin/bash

# Simple execution script for Commercial-View Excellence Resolution
echo "🚀 Commercial-View Excellence Resolution"
echo "========================================"
echo ""

# Change to repository directory
cd /Users/jenineferderas/Commercial-View

# Use virtual environment Python if available
if [ -f ".venv/bin/python" ]; then
    echo "Using virtual environment Python..."
    .venv/bin/python execute_complete_resolution.py
else
    echo "Using system Python..."
    python3 execute_complete_resolution.py
fi

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Resolution completed successfully!"
else
    echo ""
    echo "⚠️  Resolution encountered issues. Check execution_log.json for details."
fi

exit $EXIT_CODE
