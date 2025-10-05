#!/usr/bin/env python3
"""
Setup script to fix project issues and prepare development environment.
"""

import os
import sys
import subprocess
import re
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return its output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip() and not check:
        print(f"Error: {result.stderr.strip()}")
    return result.returncode == 0

def kill_port_processes(port):
    """Kill processes using the specified port."""
    print(f"Checking for processes on port {port}...")
    try:
        # Find PIDs
        result = subprocess.run(
            ["lsof", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"], 
            capture_output=True, text=True, check=False
        )
        pids = result.stdout.strip().split('\n')
        
        # Kill each PID
        for pid in pids:
            if pid:
                print(f"Killing process {pid} using port {port}")
                run_command(["kill", "-9", pid], check=False)
        return True
    except Exception as e:
        print(f"Error killing processes on port {port}: {str(e)}")
        return False

def fix_data_loader():
    """Fix the data_loader.py file."""
    data_loader_path = Path(__file__).parent / "src" / "data_loader.py"
    print(f"Fixing {data_loader_path}...")
    
    # New content for data_loader.py
    content = '''from __future__ import annotations
from pathlib import Path
from typing import Union, Dict
import pandas as pd

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _resolve_base_path(base: Union[str, Path, None] = None) -> Path:
    return Path(base).resolve() if base else _DEFAULT_DATA_DIR

PRICING_FILENAMES: Dict[str, str] = {
    "loan_data": "loan_data.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "payment_schedule": "payment_schedule.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv",
}

def _read_csv(path_or_dir: Union[str, Path], default_name: str | None = None) -> pd.DataFrame:
    p = Path(path_or_dir)
    if p.is_dir():
        if not default_name:
            raise ValueError("Directory provided without default_name.")
        p = p / default_name
    return pd.read_csv(p)

def load_loan_data(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["loan_data"])

def load_historic_real_payment(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["historic_real_payment"])

def load_payment_schedule(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["payment_schedule"])

def load_customer_data(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["customer_data"])

def load_collateral(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["collateral"])

__all__ = [
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral",
    "_resolve_base_path",
    "PRICING_FILENAMES",
]
'''
    
    # Write the new content
    try:
        os.makedirs(os.path.dirname(data_loader_path), exist_ok=True)
        with open(data_loader_path, 'w') as f:
            f.write(content)
        print("✅ data_loader.py file fixed!")
        return True
    except Exception as e:
        print(f"Error fixing data_loader.py: {str(e)}")
        return False

def fix_requirements():
    """Fix the httpx version conflict in requirements-dev.txt."""
    req_dev_path = Path(__file__).parent / "requirements-dev.txt"
    
    if not req_dev_path.exists():
        print("⚠️ requirements-dev.txt not found. Skipping fix.")
        return True
    
    print(f"Fixing httpx version in {req_dev_path}...")
    
    try:
        # Read the current content
        with open(req_dev_path, 'r') as f:
            content = f.read()
        
        # Replace the httpx version
        updated_content = re.sub(
            r'httpx>=0\.28\.1', 
            'httpx==0.25.1',
            content
        )
        
        # Write back
        with open(req_dev_path, 'w') as f:
            f.write(updated_content)
            
        print("✅ httpx version fixed in requirements-dev.txt!")
        return True
    except Exception as e:
        print(f"Error fixing requirements-dev.txt: {str(e)}")
        return False

def install_dependencies():
    """Install dependencies from requirements files."""
    req_path = Path(__file__).parent / "requirements.txt"
    req_dev_path = Path(__file__).parent / "requirements-dev.txt"
    
    if not req_path.exists():
        print("⚠️ requirements.txt not found. Cannot install dependencies.")
        return False
    
    print("Installing dependencies...")
    
    # Install runtime dependencies
    success = run_command(["pip", "install", "-r", str(req_path)])
    
    # Install dev dependencies if they exist
    if req_dev_path.exists() and success:
        success = run_command(["pip", "install", "-r", str(req_dev_path)])
        
    if success:
        print("✅ Dependencies installed successfully!")
    return success

def run_tests():
    """Run tests to verify setup."""
    print("Running sanity check...")
    run_command([
        "python", "-c", 
        "import src.data_loader as m; print(m.__all__)"
    ])
    
    print("\nRunning tests...")
    return run_command(["pytest", "-q"])

def run_app(port=8001):
    """Run the FastAPI app."""
    print(f"\nStarting app on port {port}...")
    run_command(["uvicorn", "run:app", "--reload", f"--port={port}"])

def main():
    """Main function to run all setup steps."""
    print("="*80)
    print("Commercial View Project Setup")
    print("="*80)
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ Virtual environment not detected!")
        print("Please run: source .venv/bin/activate")
        return False
    
    # Kill any running servers
    kill_port_processes(8000)
    kill_port_processes(8001)
    
    # Fix data_loader.py
    if not fix_data_loader():
        return False
    
    # Fix requirements
    if not fix_requirements():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Run tests
    if not run_tests():
        print("⚠️ Some tests failed, but continuing...")
    
    # Ask to run the app
    run_app_input = input("\nDo you want to run the app now? (y/n): ")
    if run_app_input.lower() == 'y':
        port_input = input("Port to use (default: 8001): ")
        port = int(port_input) if port_input.strip().isdigit() else 8001
        run_app(port)
    else:
        print("\nSetup complete! Run the app later with:")
        print("uvicorn run:app --reload --port=8001")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
