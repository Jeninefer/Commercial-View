#!/usr/bin/env python3
"""
Manage Jupyter kernels for Commercial-View development
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List

class KernelManager:
    """Manage Jupyter kernels for Commercial-View"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.kernel_name = "commercial-view"
        
    def create_kernel_spec(self) -> Dict:
        """Create kernel specification for Commercial-View"""
        return {
            "argv": [
                str(self.project_root / ".venv" / "bin" / "python"),
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
                "COMMERCIAL_VIEW_ROOT": str(self.project_root),
                "PYTHONPATH": str(self.project_root / "src"),
                "ENVIRONMENT": "development",
                "DEBUG": "true"
            }
        }
    
    def install_kernel(self) -> bool:
        """Install Commercial-View kernel"""
        try:
            # Create temporary kernel directory
            temp_kernel_dir = self.project_root / "temp_kernel"
            temp_kernel_dir.mkdir(exist_ok=True)
            
            # Write kernel.json
            kernel_json = temp_kernel_dir / "kernel.json"
            with open(kernel_json, 'w', encoding='utf-8') as f:
                json.dump(self.create_kernel_spec(), f, indent=2)
            
            # Install kernel
            cmd = [
                sys.executable, "-m", "jupyter", "kernelspec", "install",
                str(temp_kernel_dir), "--user", "--name", self.kernel_name
            ]
            
            print(f"🔧 Installing {self.kernel_name} kernel...")
            subprocess.run(cmd, check=True)
            
            # Cleanup
            kernel_json.unlink()
            temp_kernel_dir.rmdir()
            
            print("✅ Commercial-View kernel installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install kernel: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def uninstall_kernel(self) -> bool:
        """Uninstall Commercial-View kernel"""
        try:
            cmd = [
                sys.executable, "-m", "jupyter", "kernelspec", "remove",
                self.kernel_name, "-f"
            ]
            
            print(f"🗑️ Removing {self.kernel_name} kernel...")
            subprocess.run(cmd, check=True)
            print("✅ Commercial-View kernel removed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove kernel: {e}")
            return False
    
    def list_kernels(self) -> List[str]:
        """List all available kernels"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "jupyter", "kernelspec", "list"
            ], capture_output=True, text=True, check=True)
            
            print("📋 Available Jupyter kernels:")
            print(result.stdout)
            return result.stdout.split('\n')
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to list kernels: {e}")
            return []
    
    def kernel_exists(self) -> bool:
        """Check if Commercial-View kernel exists"""
        kernels = self.list_kernels()
        return any(self.kernel_name in line for line in kernels)

def main():
    """Main kernel management function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Commercial-View Jupyter kernels")
    parser.add_argument("action", choices=["install", "uninstall", "list", "check"],
                       help="Action to perform")
    
    args = parser.parse_args()
    manager = KernelManager()
    
    if args.action == "install":
        success = manager.install_kernel()
    elif args.action == "uninstall":
        success = manager.uninstall_kernel()
    elif args.action == "list":
        manager.list_kernels()
        success = True
    elif args.action == "check":
        exists = manager.kernel_exists()
        print(f"Commercial-View kernel exists: {exists}")
        success = True
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
