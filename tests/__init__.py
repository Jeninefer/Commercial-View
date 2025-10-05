"""Test package for Commercial View.

IMPORTANT: Always use the virtual environment Python when running tests:

    # CORRECT (notice the initial activation)
    source .venv/bin/activate
    python -m pytest tests/
    # or
    pytest tests/

    # INCORRECT (will fail with import errors)
    /opt/homebrew/bin/python3 -m pytest tests/

Common errors when using the wrong Python interpreter:
- ModuleNotFoundError: No module named 'pytest'
- ModuleNotFoundError: No module named 'pandas'
"""

import os
import sys
from pathlib import Path

# Add the project root to sys.path to enable importing from src
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Print warning if not using virtual environment
if not os.environ.get('VIRTUAL_ENV'):
    print("\033[93mWARNING: You are not using the virtual environment. "
          "Tests may fail due to missing dependencies.\033[0m")
    print("\033[93mRun 'source .venv/bin/activate' first.\033[0m")
