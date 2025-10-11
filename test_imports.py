"""Test script to verify all imports work correctly"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")
print("=" * 50)

try:
    from src import __version__
    print(f"✅ src package imported successfully (version: {__version__})")
except Exception as e:
    print(f"❌ Failed to import src: {e}")

try:
    from src.data_loader import DataLoader
    print("✅ DataLoader imported successfully")
except Exception as e:
    print(f"❌ Failed to import DataLoader: {e}")

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
except Exception as e:
    print(f"❌ Failed to import FastAPI: {e}")

try:
    import pandas as pd
    print(f"✅ Pandas imported successfully (version: {pd.__version__})")
except Exception as e:
    print(f"❌ Failed to import Pandas: {e}")

try:
    import yaml
    print("✅ YAML imported successfully")
except Exception as e:
    print(f"❌ Failed to import YAML: {e}")

print("=" * 50)
print("Import test completed!")
