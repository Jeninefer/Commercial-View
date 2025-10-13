#!/bin/bash
# Commercial-View API Startup Script

PORTFOLIO_VALUE="\$208,192,588.65"
echo "🚀 Starting Commercial-View API..."
echo "Portfolio: ${PORTFOLIO_VALUE} Abaco dataset (48,853 records)"
echo "Features: Spanish client support, USD factoring validation"

# Check if uvicorn is installed with [standard] extras and correct version
REQUIRED_UVICORN_VERSION="0.23.2"
UVICORN_VERSION=$(pip show uvicorn 2>/dev/null | grep ^Version: | awk '{print $2}')

# Check for a module only present with [standard] extras (e.g., 'watchgod')
python -c "import uvicorn; import watchgod" 2>/dev/null
UVICORN_STANDARD=$?

# Ensure 'packaging' module is installed for version comparison
python -c "import packaging" 2>/dev/null || pip install packaging
# Use Python's packaging.version to compare versions (allows newer versions)
python -c "import sys; from packaging.version import Version; sys.exit(0 if not '$UVICORN_VERSION' or Version('$UVICORN_VERSION') < Version('$REQUIRED_UVICORN_VERSION') else 1)" 2>/dev/null
UVICORN_VERSION_OLD=$?

if [ -z "$UVICORN_VERSION" ] || [ "$UVICORN_STANDARD" -ne 0 ] || [ "$UVICORN_VERSION_OLD" -eq 0 ]; then
    echo "❌ uvicorn[standard] (version $REQUIRED_UVICORN_VERSION or newer) not found or incomplete. Installing/upgrading..."
    pip install "uvicorn[standard]>=$REQUIRED_UVICORN_VERSION"
else
    echo "✅ uvicorn[standard] (version $UVICORN_VERSION) is installed."
fi

# Start the API server
echo "✅ Starting FastAPI server on http://localhost:8000"
uvicorn run:app --reload --host 0.0.0.0 --port 8000
