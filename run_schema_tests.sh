#!/bin/bash

echo "================================"
echo "Schema Parser Test Suite"
echo "================================"

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Check if schema file exists
if [ ! -f "Downloads/abaco_schema_autodetected.json" ]; then
    echo "❌ Schema file not found at Downloads/abaco_schema_autodetected.json"
    echo "Please ensure the file exists in the correct location."
    exit 1
fi

echo ""
echo "Running comprehensive tests..."
python3 test_schema_parser.py

echo ""
echo "Running usage examples..."
python3 examples/schema_usage_example.py

echo ""
echo "Testing CLI interface..."
python3 -m src.utils.schema_parser Downloads/abaco_schema_autodetected.json --summary

echo ""
echo "✅ All tests complete!"
