#!/usr/bin/env python3
"""
Enhanced Jupyter startup script for Commercial-View development
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_jupyter_environment():
    """Setup Commercial-View environment for Jupyter"""
    project_root = Path(__file__).parent.parent
    
    # Set environment variables
    os.environ["COMMERCIAL_VIEW_ROOT"] = str(project_root)
    os.environ["PYTHONPATH"] = f"{project_root}/src:{os.environ.get('PYTHONPATH', '')}"
    
    # Load .env file if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file, encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    print("🚀 Commercial-View Jupyter environment configured")
    print(f"📁 Project root: {project_root}")

def start_jupyter_lab():
    """Start Jupyter Lab with Commercial-View configuration"""
    setup_jupyter_environment()
    
    try:
        # Start Jupyter Lab
        cmd = [
            "jupyter", "lab",
            "--notebook-dir", ".",
            "--ip", "0.0.0.0",
            "--port", "8888",
            "--no-browser",
            "--allow-root"
        ]
        
        print("🔬 Starting Jupyter Lab for Commercial-View...")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Jupyter Lab stopped")
    except FileNotFoundError:
        print("❌ Jupyter not installed. Install with: pip install jupyterlab")

if __name__ == "__main__":
    start_jupyter_lab()
