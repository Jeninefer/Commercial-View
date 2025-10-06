#!/usr/bin/env python3
"""
Install Commercial-View Jupyter kernel
"""

import json
import os
import sys
from pathlib import Path
import subprocess

def install_commercial_view_kernel():
    """Install the Commercial-View kernel for Jupyter"""
    project_root = Path(__file__).parent.parent
    
    # Kernel specification
    kernel_spec = {
        "argv": [
            str(project_root / ".venv" / "bin" / "python"),
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}"
        ],
        "display_name": "Commercial-View Python",
        "language": "python",
        "metadata": {
            "debugger": True
        },
        "env": {
            "COMMERCIAL_VIEW_ROOT": str(project_root),
            "PYTHONPATH": str(project_root / "src"),
            "ENVIRONMENT": "development",
            "DEBUG": "true"
        }
    }
    
    try:
        # Install the kernel
        cmd = [
            sys.executable, "-m", "jupyter", "kernelspec", "install-self",
            "--user", "--name", "commercial-view"
        ]
        
        # Create temporary kernel.json
        kernel_json_path = project_root / "kernel.json"
        with open(kernel_json_path, 'w', encoding='utf-8') as f:
            json.dump(kernel_spec, f, indent=2)
        
        print("🔧 Installing Commercial-View Jupyter kernel...")
        subprocess.run(cmd, check=True)
        
        print("✅ Commercial-View kernel installed successfully!")
        print("📝 Kernel name: commercial-view")
        print("🚀 Start Jupyter with: jupyter lab")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install kernel: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = install_commercial_view_kernel()
    sys.exit(0 if success else 1)
