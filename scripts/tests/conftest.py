"""Test configuration for Commercial View application.

⚠️ ENVIRONMENT SETUP INSTRUCTIONS ⚠️
-----------------------------------
You're seeing this error because you're using system Python (/opt/homebrew/bin/python3)
instead of the project's virtual environment Python.

TO FIX THIS, COPY-PASTE THESE EXACT COMMANDS:

cd /Users/jenineferderas/Documents/GitHub/Commercial-View
source .venv/bin/activate
pytest tests/
"""

import os
import sys
from pathlib import Path

from scripts.utils.env_check import check_virtualenv

# Check if running in virtual environment
check_virtualenv()

# Try importing pytest with helpful error message
try:
    import pytest
except ImportError:
    print("\n" + "=" * 80)
    print("\033[91m⚠️  ERROR: PYTEST NOT INSTALLED ⚠️\033[0m")
    print("=" * 80)
    print("\033[93mYou need to install pytest in your virtual environment.\033[0m")
    print("\033[93mCopy and paste these commands:\033[0m")
    print("\033[92m  cd /Users/jenineferderas/Documents/GitHub/Commercial-View\033[0m")
    print("\033[92m  source .venv/bin/activate\033[0m")
    print("\033[92m  pip install pytest\033[0m")
    print("\033[92m  pytest tests/\033[0m")
    print("=" * 80 + "\n")
    sys.exit(1)

# Add the project root to the path so imports work properly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure test environment
@pytest.fixture(scope="session", autouse=True)
def configure_env():
    """Configure environment variables for testing."""
    os.environ["COMMERCIAL_VIEW_DATA_PATH"] = str(project_root / "tests" / "data")

    # Create test data directory if it doesn't exist
    test_data_dir = project_root / "tests" / "data"
    test_data_dir.mkdir(exist_ok=True)

    yield
