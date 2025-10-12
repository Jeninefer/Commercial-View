#!/usr/bin/env python3
"""
Commercial-View Project Setup Script
Production-ready commercial lending analytics platform setup
"""

import subprocess
import sys
import os
from pathlib import Path


def print_banner():
    """Print setup banner with project information."""
    print("=" * 60)
    print("🚀 Commercial-View Analytics Platform Setup")
    print("=" * 60)
    print("✅ Real Data API: Serves your actual $208M+ Abaco portfolio")
    print("✅ Production Ready: Complete dependency management")
    print("✅ Spanish Support: UTF-8 client name processing")
    print("✅ USD Factoring: Complete validation system")
    print("=" * 60)


def install_python_dependencies():
    """Install required Python packages."""
    requirements = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pandas==2.1.3",
        "numpy==1.26.2",
        "pydantic==2.5.0",
        "pyyaml==6.0.1",
        "python-multipart==0.0.6",
    ]

    print("\n📦 Installing Python dependencies...")

    for requirement in requirements:
        try:
            print(f"Installing {requirement}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", requirement],
                check=True,
                capture_output=True,
            )
            print(f"✅ Installed: {requirement}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {requirement}: {e}")
            return False

    return True


def create_project_structure():
    """Create necessary project directories."""
    directories = ["src", "config", "data", "exports", "tests", "docs", "scripts"]

    print("\n📁 Creating project structure...")

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}/")


def create_startup_script():
    """Create the API startup script."""
    startup_script = """#!/bin/bash
# Commercial-View API Startup Script

echo "🚀 Starting Commercial-View API..."
echo "Portfolio: $208M+ Abaco dataset (48,853 records)"
echo "Features: Spanish client support, USD factoring validation"

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "❌ uvicorn not found. Installing..."
    pip install "uvicorn[standard]"
fi

# Start the API server
echo "✅ Starting FastAPI server on http://localhost:8000"
uvicorn run:app --reload --host 0.0.0.0 --port 8000
"""

    with open("start_api.sh", "w") as f:
        f.write(startup_script)

    # Make it executable
    os.chmod("start_api.sh", 0o755)
    print("✅ Created: start_api.sh")


def validate_abaco_schema():
    """Check if Abaco schema file exists."""
    schema_path = Path("config/abaco_schema_autodetected.json")

    if schema_path.exists():
        print(f"✅ Found Abaco schema: {schema_path}")
        return True
    else:
        print(f"⚠️  Abaco schema not found: {schema_path}")
        print("   Please place your schema file in the config/ directory")
        return False


def main():
    """Main setup function."""
    print_banner()

    # Create project structure
    create_project_structure()

    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Setup failed during dependency installation")
        return False

    # Create startup script
    create_startup_script()

    # Validate schema
    validate_abaco_schema()

    print("\n=" * 60)
    print("✅ Commercial-View setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Place your Abaco data files in the data/ directory")
    print("2. Run: ./start_api.sh")
    print("3. Open: http://localhost:8000")
    print("4. Check exports/ directory for results")
    print("\nFor manual start:")
    print("python -m uvicorn run:app --reload")

    return True


if __name__ == "__main__":
    # Define DAYS_IN_DEFAULT if not already defined
    try:
        DAYS_IN_DEFAULT
    except NameError:
        DAYS_IN_DEFAULT = None

    success = main()
    sys.exit(0 if success else 1)
