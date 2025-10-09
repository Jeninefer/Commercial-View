#!/usr/bin/env python3
"""
<<<<<<< HEAD
Enhanced Jupyter kernel management for Commercial-View commercial lending development
=======
Manage Jupyter kernels for Commercial-View development
>>>>>>> 9039104 (Add missing project files and documentation)
"""

import json
import os
import sys
import subprocess
<<<<<<< HEAD
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CommercialViewKernelManager:
    """Enhanced Jupyter kernel manager for Commercial-View commercial lending platform"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.kernel_name = "commercial-view"
        self.venv_path = self.project_root / ".venv"

    def validate_environment(self) -> Tuple[bool, List[str]]:
        """Validate Commercial-View development environment"""
        issues = []

        # Check virtual environment
        if not self.venv_path.exists():
            issues.append("Virtual environment not found at .venv")

        # Check Python executable
        python_exe = self.venv_path / "bin" / "python"
        if not python_exe.exists():
            issues.append("Python executable not found in virtual environment")

        # Check required packages
        required_packages = ["ipykernel", "jupyter", "pandas", "numpy"]
        for package in required_packages:
            try:
                subprocess.run(
                    [str(python_exe), "-c", f"import {package}"],
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                issues.append(f"Required package '{package}' not installed")

        # Check Commercial-View specific files
        critical_files = [
            "src/main.py",
            "configs/pricing_config.yml",
            "configs/dpd_policy.yml",
        ]

        for file_path in critical_files:
            if not (self.project_root / file_path).exists():
                issues.append(f"Critical file missing: {file_path}")

        return len(issues) == 0, issues

    def create_kernel_spec(self) -> Dict:
        """Create enhanced kernel specification for Commercial-View"""
        python_exe = self.venv_path / "bin" / "python"

        return {
            "argv": [
                str(python_exe),
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Commercial-View (Commercial Lending)",
            "language": "python",
            "metadata": {
                "debugger": True,
                "commercial_view": {
                    "version": "1.0.0",
                    "platform": "commercial_lending",
                    "features": [
                        "pricing_models",
                        "dpd_analysis",
                        "kpi_generation",
                        "risk_assessment",
                        "portfolio_analytics",
                    ],
                },
            },
            "env": {
                "COMMERCIAL_VIEW_ROOT": str(self.project_root),
                "PYTHONPATH": f"{self.project_root / 'src'}:{self.project_root / 'scripts'}",
                "ENVIRONMENT": "development",
                "DEBUG": "true",
                "COMMERCIAL_VIEW_MODE": "jupyter",
                "PRICING_CONFIG_PATH": str(
                    self.project_root / "configs" / "pricing_config.yml"
                ),
                "DPD_POLICY_PATH": str(
                    self.project_root / "configs" / "dpd_policy.yml"
                ),
                "COLUMN_MAPS_PATH": str(
                    self.project_root / "configs" / "column_maps.yml"
                ),
                "JUPYTER_ENABLE_LAB": "yes",
            },
        }

    def install_kernel(self, force: bool = False) -> bool:
        """Install Commercial-View kernel with validation"""
        print("🏦 Installing Commercial-View Commercial Lending Jupyter Kernel...")

        # Validate environment
        is_valid, issues = self.validate_environment()

        if not is_valid:
            print("❌ Environment validation failed:")
            for issue in issues:
                print(f"   - {issue}")
            print("\n💡 Fix these issues before installing the kernel")
            return False

        print("✅ Environment validation passed")

        # Check if kernel already exists
        if not force and self.kernel_exists():
            print(f"⚠️  Kernel '{self.kernel_name}' already exists")
            response = input("Overwrite existing kernel? (y/N): ")
            if response.lower() != "y":
                return False

            # Remove existing kernel
            self.uninstall_kernel()

=======
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
>>>>>>> 9039104 (Add missing project files and documentation)
        try:
            # Create temporary kernel directory
            temp_kernel_dir = self.project_root / "temp_kernel"
            temp_kernel_dir.mkdir(exist_ok=True)
<<<<<<< HEAD

            # Write kernel.json
            kernel_json = temp_kernel_dir / "kernel.json"
            with open(kernel_json, "w", encoding="utf-8") as f:
                json.dump(self.create_kernel_spec(), f, indent=2)

            # Create logo files for Commercial-View branding
            self.create_kernel_logos(temp_kernel_dir)

            # Install kernel
            python_exe = self.venv_path / "bin" / "python"
            cmd = [
                str(python_exe),
                "-m",
                "jupyter",
                "kernelspec",
                "install",
                str(temp_kernel_dir),
                "--user",
                "--name",
                self.kernel_name,
            ]

            print(f"🔧 Installing {self.kernel_name} kernel...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Cleanup temporary directory
            shutil.rmtree(temp_kernel_dir)

            print("✅ Commercial-View kernel installed successfully!")
            print("🏦 Features enabled:")
            print("   - Commercial loan pricing models")
            print("   - Days Past Due (DPD) analysis")
            print("   - KPI generation and reporting")
            print("   - Portfolio risk assessment")
            print("   - Regulatory compliance tools")

            # Create startup notebook
            self.create_startup_notebook()

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install kernel: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
=======
            
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
>>>>>>> 9039104 (Add missing project files and documentation)
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
<<<<<<< HEAD

    def create_kernel_logos(self, kernel_dir: Path) -> None:
        """Create Commercial-View branded logo files for the kernel"""
        # Create simple text-based logos (in production, these would be actual image files)
        logo_64_content = """
🏦 Commercial-View
   Commercial Lending Analytics
        """

        logo_32_content = "🏦 CV"

        # Write logo files
        (kernel_dir / "logo-64x64.txt").write_text(logo_64_content)
        (kernel_dir / "logo-32x32.txt").write_text(logo_32_content)

    def create_startup_notebook(self) -> None:
        """Create a startup notebook with Commercial-View examples"""
        notebooks_dir = self.project_root / "notebooks"
        notebooks_dir.mkdir(exist_ok=True)

        startup_notebook = notebooks_dir / "commercial_view_startup.ipynb"

        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# Commercial-View Commercial Lending Analytics\n",
                        "\n",
                        "Welcome to the Commercial-View Jupyter environment for commercial lending analytics.\n",
                        "\n",
                        "## Available Features\n",
                        "- 🏦 Commercial loan pricing models\n",
                        "- 📊 Days Past Due (DPD) analysis\n",
                        "- 📈 KPI generation and reporting\n",
                        "- ⚖️ Portfolio risk assessment\n",
                        "- 📋 Regulatory compliance tools",
                    ],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Import Commercial-View modules\n",
                        "import sys\n",
                        "import os\n",
                        "from pathlib import Path\n",
                        "\n",
                        "# Add Commercial-View to Python path\n",
                        "project_root = Path(os.getcwd())\n",
                        "if 'COMMERCIAL_VIEW_ROOT' in os.environ:\n",
                        "    project_root = Path(os.environ['COMMERCIAL_VIEW_ROOT'])\n",
                        "\n",
                        "sys.path.insert(0, str(project_root / 'src'))\n",
                        "\n",
                        'print(f"📁 Commercial-View project root: {project_root}")\n',
                        'print(f"🐍 Python version: {sys.version}")\n',
                        "print(f\"🏦 Environment: {os.environ.get('ENVIRONMENT', 'unknown')}\")",
                    ],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Import standard data science libraries\n",
                        "import pandas as pd\n",
                        "import numpy as np\n",
                        "import matplotlib.pyplot as plt\n",
                        "import seaborn as sns\n",
                        "\n",
                        "# Configure plotting\n",
                        "plt.style.use('default')\n",
                        "sns.set_palette('husl')\n",
                        "\n",
                        'print("📊 Data science libraries loaded")\n',
                        'print(f"🐼 Pandas version: {pd.__version__}")\n',
                        'print(f"🔢 NumPy version: {np.__version__}")',
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Commercial Lending Quick Start\n",
                        "\n",
                        "### Load Sample Commercial Loan Data",
                    ],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Load Commercial-View configuration\n",
                        "import yaml\n",
                        "\n",
                        "config_files = {\n",
                        "    'pricing': project_root / 'configs' / 'pricing_config.yml',\n",
                        "    'dpd': project_root / 'configs' / 'dpd_policy.yml',\n",
                        "    'columns': project_root / 'configs' / 'column_maps.yml'\n",
                        "}\n",
                        "\n",
                        "configs = {}\n",
                        "for name, path in config_files.items():\n",
                        "    if path.exists():\n",
                        "        with open(path, 'r') as f:\n",
                        "            configs[name] = yaml.safe_load(f)\n",
                        '        print(f"✅ Loaded {name} configuration")\n',
                        "    else:\n",
                        '        print(f"⚠️  Configuration file not found: {path}")\n',
                        "\n",
                        'print(f"\\n🔧 Loaded {len(configs)} configuration files")',
                    ],
                },
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Commercial-View (Commercial Lending)",
                    "language": "python",
                    "name": "commercial-view",
                },
                "language_info": {"name": "python", "version": "3.8.0"},
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        with open(startup_notebook, "w") as f:
            json.dump(notebook_content, f, indent=2)

        print(f"📓 Created startup notebook: {startup_notebook}")

    def uninstall_kernel(self) -> bool:
        """Uninstall Commercial-View kernel"""
        try:
            python_exe = self.venv_path / "bin" / "python"
            cmd = [
                str(python_exe),
                "-m",
                "jupyter",
                "kernelspec",
                "remove",
                self.kernel_name,
                "-f",
            ]

=======
    
    def uninstall_kernel(self) -> bool:
        """Uninstall Commercial-View kernel"""
        try:
            cmd = [
                sys.executable, "-m", "jupyter", "kernelspec", "remove",
                self.kernel_name, "-f"
            ]
            
>>>>>>> 9039104 (Add missing project files and documentation)
            print(f"🗑️ Removing {self.kernel_name} kernel...")
            subprocess.run(cmd, check=True)
            print("✅ Commercial-View kernel removed successfully!")
            return True
<<<<<<< HEAD

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove kernel: {e}")
            return False

    def list_kernels(self) -> List[str]:
        """List all available kernels with enhanced formatting"""
        try:
            python_exe = self.venv_path / "bin" / "python"
            result = subprocess.run(
                [str(python_exe), "-m", "jupyter", "kernelspec", "list"],
                capture_output=True,
                text=True,
                check=True,
            )

            print("📋 Available Jupyter kernels:")
            print(result.stdout)

            # Highlight Commercial-View kernel if present
            lines = result.stdout.split("\n")
            for line in lines:
                if self.kernel_name in line:
                    print(f"🏦 Commercial-View kernel found: {line.strip()}")
                    break

            return lines

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to list kernels: {e}")
            return []

    def kernel_exists(self) -> bool:
        """Check if Commercial-View kernel exists"""
        try:
            python_exe = self.venv_path / "bin" / "python"
            result = subprocess.run(
                [str(python_exe), "-m", "jupyter", "kernelspec", "list"],
                capture_output=True,
                text=True,
                check=True,
            )

            return self.kernel_name in result.stdout
        except subprocess.CalledProcessError:
            return False

    def get_kernel_info(self) -> Optional[Dict]:
        """Get detailed information about the Commercial-View kernel"""
        if not self.kernel_exists():
            return None

        try:
            python_exe = self.venv_path / "bin" / "python"
            result = subprocess.run(
                [str(python_exe), "-m", "jupyter", "kernelspec", "list", "--json"],
                capture_output=True,
                text=True,
                check=True,
            )

            kernels_data = json.loads(result.stdout)
            return kernels_data.get("kernelspecs", {}).get(self.kernel_name)

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None

    def setup_jupyter_extensions(self) -> bool:
        """Setup Jupyter extensions for Commercial-View development"""
        print("🔧 Setting up Jupyter extensions for Commercial-View...")

        extensions = [
            "jupyterlab-git",
            "jupyterlab_code_formatter",
            "@jupyter-widgets/jupyterlab-manager",
        ]

        try:
            python_exe = self.venv_path / "bin" / "python"

            for extension in extensions:
                print(f"📦 Installing {extension}...")
                subprocess.run(
                    [str(python_exe), "-m", "pip", "install", extension],
                    check=True,
                    capture_output=True,
                )

            print("✅ Jupyter extensions installed successfully!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Some extensions may have failed to install: {e}")
            return False


def main():
    """Enhanced main kernel management function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage Commercial-View Jupyter kernels for commercial lending development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s install              # Install Commercial-View kernel
  %(prog)s install --force      # Force reinstall kernel
  %(prog)s uninstall            # Remove Commercial-View kernel
  %(prog)s list                 # List all kernels
  %(prog)s check                # Check kernel status
  %(prog)s info                 # Show kernel details
  %(prog)s setup-extensions     # Install Jupyter extensions
        """,
    )

    parser.add_argument(
        "action",
        choices=["install", "uninstall", "list", "check", "info", "setup-extensions"],
        help="Action to perform",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force reinstall (for install action)"
    )

    args = parser.parse_args()
    manager = CommercialViewKernelManager()

    print("🏦 Commercial-View Kernel Manager")
    print("=" * 50)

    success = True

    if args.action == "install":
        success = manager.install_kernel(force=args.force)
=======
            
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
>>>>>>> 9039104 (Add missing project files and documentation)
    elif args.action == "uninstall":
        success = manager.uninstall_kernel()
    elif args.action == "list":
        manager.list_kernels()
<<<<<<< HEAD
    elif args.action == "check":
        exists = manager.kernel_exists()
        print(f"🔍 Commercial-View kernel exists: {'✅ Yes' if exists else '❌ No'}")
        if exists:
            print("💡 Use 'info' action for detailed kernel information")
    elif args.action == "info":
        info = manager.get_kernel_info()
        if info:
            print("📋 Commercial-View Kernel Information:")
            print(f"   Display name: {info.get('spec', {}).get('display_name', 'N/A')}")
            print(f"   Language: {info.get('spec', {}).get('language', 'N/A')}")
            print(f"   Resource dir: {info.get('resource_dir', 'N/A')}")
        else:
            print("❌ Commercial-View kernel not found or information unavailable")
            success = False
    elif args.action == "setup-extensions":
        success = manager.setup_jupyter_extensions()

    if success:
        print("\n🎉 Operation completed successfully!")
        if args.action == "install":
            print("💡 Next steps:")
            print("   1. Start Jupyter: jupyter lab")
            print("   2. Open notebooks/commercial_view_startup.ipynb")
            print("   3. Select 'Commercial-View (Commercial Lending)' kernel")

    return 0 if success else 1


=======
        success = True
    elif args.action == "check":
        exists = manager.kernel_exists()
        print(f"Commercial-View kernel exists: {exists}")
        success = True
    
    return 0 if success else 1

>>>>>>> 9039104 (Add missing project files and documentation)
if __name__ == "__main__":
    sys.exit(main())
