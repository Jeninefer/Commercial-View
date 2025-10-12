#!/bin/bash

# Install Missing Dependencies for Commercial-View Abaco Integration
# Adds psutil and other production dependencies

echo "📦 Commercial-View Missing Dependencies Installation"
echo "48,853 Records | System Monitoring | Production Ready"
echo "====================================================="

# Detect platform and virtual environment
if [[ "$OSTYPE" == "darwin"* ]]; then
    VENV_PYTHON="./.venv/bin/python"
    VENV_PIP="./.venv/bin/pip"
    echo "🍎 macOS environment detected"
else
    VENV_PYTHON="./.venv/Scripts/python.exe"
    VENV_PIP="./.venv/Scripts/pip.exe"
    echo "🪟 Windows environment detected"
fi

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

echo "✅ Virtual environment found: $VENV_PYTHON"

# Install missing psutil dependency
echo ""
echo "📦 Installing missing psutil dependency..."
$VENV_PIP install psutil>=5.9.0

# Install additional production monitoring dependencies
echo ""
echo "📦 Installing additional production dependencies..."
$VENV_PIP install python-dotenv>=1.0.0
$VENV_PIP install colorama>=0.4.6

# Update requirements.txt
echo ""
echo "📄 Updating requirements.txt..."
echo "psutil>=5.9.0" >> requirements.txt
echo "python-dotenv>=1.0.0" >> requirements.txt
echo "colorama>=0.4.6" >> requirements.txt

# Verify installations
echo ""
echo "🧪 Verifying installations..."
$VENV_PYTHON -c "
import psutil
import dotenv
import colorama
print('✅ psutil version:', psutil.__version__)
print('✅ python-dotenv available')
print('✅ colorama available')
print('✅ All dependencies successfully installed')
"

echo ""
echo "✅ Missing dependencies installation completed!"
echo "🎯 Ready for Commercial-View PowerShell validation"
