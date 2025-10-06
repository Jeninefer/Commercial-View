#!/usr/bin/env python3
"""
Enhanced IPython startup script for Commercial-View development
"""

import os
import sys
from pathlib import Path

def setup_commercial_view_environment():
    """Setup Commercial-View specific environment for IPython"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))
    
    # Set environment variables
    os.environ["COMMERCIAL_VIEW_ROOT"] = str(project_root)
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "true"
    
    # Load .env file if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                    except ValueError:
                        continue
    
    print("🚀 Commercial-View development environment loaded")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path includes: {project_root}/src")

def start_enhanced_ipython():
    """Start IPython with Commercial-View enhancements"""
    
    setup_commercial_view_environment()
    
    try:
        from IPython import start_ipython
        
        # IPython startup banner
        banner = """
🏦 Commercial-View Development Shell
=====================================
Available imports:
  import pandas as pd
  import numpy as np
  from src.api import app
  from src.data_loader import DataLoader

Quick commands:
  %load_ext autoreload
  %autoreload 2
        """
        
        # Pre-import common modules
        user_ns = {
            'pd': __import__('pandas'),
            'np': __import__('numpy'),
            'Path': Path,
            'os': os,
            'sys': sys
        }
        
        # Try to import project modules
        try:
            sys.path.insert(0, os.path.join(os.environ["COMMERCIAL_VIEW_ROOT"], "src"))
            user_ns['DataLoader'] = __import__('data_loader').DataLoader
        except ImportError:
            pass
        
        start_ipython(
            argv=[],
            user_ns=user_ns,
            display_banner=True,
            banner2=banner
        )
        
    except ImportError:
        print("❌ IPython not installed. Install with: pip install ipython")
        sys.exit(1)

if __name__ == "__main__":
    start_enhanced_ipython()
