#!/bin/csh
# Project-specific activation script for Commercial-View (C shell version)

# Activate virtual environment
source .venv/bin/activate.csh

# Load environment variables if .env exists
if ( -f ".env" ) then
    echo "📝 Loading environment variables from .env"
    source .env
endif

# Set project-specific paths
setenv COMMERCIAL_VIEW_ROOT "`pwd`"
if ( "$?PYTHONPATH" ) then
    setenv PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src:$PYTHONPATH"
else
    setenv PYTHONPATH "$COMMERCIAL_VIEW_ROOT/src"
endif

# Set development environment variables
setenv ENVIRONMENT "development"
setenv DEBUG "true"
if ( ! "$?API_BASE_URL" ) then
    setenv API_BASE_URL "http://localhost:8000"
endif

# Display status
echo "🚀 Commercial-View development environment ready (csh)"
echo "📁 Project root: $COMMERCIAL_VIEW_ROOT"
echo "🐍 Python path: $PYTHONPATH"
echo "💻 Virtual environment: `which python`"
echo "🌐 API Base URL: $API_BASE_URL"

# Check if required packages are installed
python -c "import fastapi" >& /dev/null
if ( $status != 0 ) then
    echo "⚠️  Missing dependencies. Run: pip install -r requirements.txt"
endif

# Create helpful aliases
alias cvapi "python server_control.py"
alias cvtest "pytest -v"
alias cvlint "python -m black src/ scripts/ && python -m mypy src/"
alias cvsync "python scripts/sync_github.py"
alias cvupload "python scripts/upload_to_drive.py"

echo "🎉 C shell environment setup complete!"
