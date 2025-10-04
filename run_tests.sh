#!/bin/bash

# Commercial-View Test Runner
# Usage: ./run_tests.sh

cd "$(dirname "$0")"

echo "================================"
echo "Commercial-View Test Suite"
echo "================================"
echo ""

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run schema parser tests
echo "Running Schema Parser Tests..."
python test_schema_parser.py

echo ""
echo "✅ Tests complete!"
deactivate
