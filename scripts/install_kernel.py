#!/usr/bin/env python3
"""
<<<<<<< HEAD
Enhanced Jupyter kernel installation for Commercial-View commercial lending platform
=======
Install Commercial-View Jupyter kernel
>>>>>>> 9039104 (Add missing project files and documentation)
"""

import json
import os
import sys
<<<<<<< HEAD
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple


def validate_environment() -> Tuple[bool, list]:
    """Validate Commercial-View environment before kernel installation"""
    project_root = Path(__file__).parent.parent
    issues = []

    # Check virtual environment
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        issues.append("Virtual environment not found at .venv")

    # Check Python executable
    python_exe = venv_path / "bin" / "python"
    if not python_exe.exists():
        issues.append("Python executable not found in virtual environment")

    # Check required packages
    required_packages = ["ipykernel", "jupyter"]
    for package in required_packages:
        try:
            subprocess.run(
                [str(python_exe), "-c", f"import {package}"],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            issues.append(f"Required package '{package}' not installed")

    # Check Commercial-View structure
    critical_paths = [
        "src/main.py",
        "configs/pricing_config.yml",
        "configs/dpd_policy.yml",
    ]

    for path in critical_paths:
        if not (project_root / path).exists():
            issues.append(f"Critical file missing: {path}")

    return len(issues) == 0, issues


def create_enhanced_kernel_spec() -> Dict:
    """Create enhanced kernel specification for Commercial-View"""
    project_root = Path(__file__).parent.parent
    python_exe = project_root / ".venv" / "bin" / "python"

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
            "COMMERCIAL_VIEW_ROOT": str(project_root),
            "PYTHONPATH": f"{project_root / 'src'}:{project_root / 'scripts'}",
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "COMMERCIAL_VIEW_MODE": "jupyter",
            "PRICING_CONFIG_PATH": str(project_root / "configs" / "pricing_config.yml"),
            "DPD_POLICY_PATH": str(project_root / "configs" / "dpd_policy.yml"),
            "COLUMN_MAPS_PATH": str(project_root / "configs" / "column_maps.yml"),
            "DATA_DIR": str(project_root / "data"),
            "EXPORT_DIR": str(project_root / "abaco_runtime" / "exports"),
        },
    }


def install_ipykernel_if_needed() -> bool:
    """Install ipykernel if not already installed"""
    project_root = Path(__file__).parent.parent
    python_exe = project_root / ".venv" / "bin" / "python"

    try:
        # Check if ipykernel is installed
        subprocess.run(
            [str(python_exe), "-c", "import ipykernel"], capture_output=True, check=True
        )
        print("✅ ipykernel already installed")
        return True
    except subprocess.CalledProcessError:
        print("📦 Installing ipykernel...")
        try:
            subprocess.run(
                [str(python_exe), "-m", "pip", "install", "ipykernel"], check=True
            )
            print("✅ ipykernel installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install ipykernel: {e}")
            return False


def create_kernel_directory() -> Optional[Path]:
    """Create temporary kernel directory with all necessary files"""
    project_root = Path(__file__).parent.parent
    kernel_dir = project_root / "temp_commercial_view_kernel"

    try:
        # Clean up existing directory
        if kernel_dir.exists():
            shutil.rmtree(kernel_dir)

        kernel_dir.mkdir(exist_ok=True)

        # Create kernel.json
        kernel_spec = create_enhanced_kernel_spec()
        kernel_json = kernel_dir / "kernel.json"
        with open(kernel_json, "w", encoding="utf-8") as f:
            json.dump(kernel_spec, f, indent=2)

        # Create kernel logo (text-based for now)
        logo_content = """
🏦 Commercial-View
Commercial Lending Analytics Platform
        """
        (kernel_dir / "logo-64x64.txt").write_text(logo_content)
        (kernel_dir / "logo-32x32.txt").write_text("🏦 CV")

        print(f"📁 Created kernel directory: {kernel_dir}")
        return kernel_dir

    except Exception as e:
        print(f"❌ Failed to create kernel directory: {e}")
        return None


def install_commercial_view_kernel() -> bool:
    """Enhanced Commercial-View kernel installation"""
    print("🏦 Installing Commercial-View Commercial Lending Jupyter Kernel")
    print("=" * 60)

    # Validate environment
    is_valid, issues = validate_environment()
    if not is_valid:
        print("❌ Environment validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Please fix these issues before installing the kernel")
        return False

    print("✅ Environment validation passed")

    # Install ipykernel if needed
    if not install_ipykernel_if_needed():
        return False

    # Create kernel directory
    kernel_dir = create_kernel_directory()
    if not kernel_dir:
        return False

    try:
        # Install the kernel
        cmd = [
            sys.executable,
            "-m",
            "jupyter",
            "kernelspec",
            "install",
            str(kernel_dir),
            "--user",
            "--name",
            "commercial-view",
        ]

        print("🔧 Installing Commercial-View Jupyter kernel...")
        subprocess.run(cmd, check=True, capture_output=True)

        # Clean up temporary directory
        shutil.rmtree(kernel_dir)

        print("✅ Commercial-View kernel installed successfully!")
        print("\n🏦 Kernel Features:")
        print("   - Commercial loan pricing models")
        print("   - Days Past Due (DPD) analysis")
        print("   - KPI generation and reporting")
        print("   - Portfolio risk assessment")
        print("   - Regulatory compliance tools")

        print("\n📝 Kernel Details:")
        print("   - Name: commercial-view")
        print("   - Display: Commercial-View (Commercial Lending)")
        print("   - Environment: Development with debugging enabled")

        print("\n🚀 Next Steps:")
        print("   1. Start Jupyter Lab: jupyter lab")
        print("   2. Create new notebook")
        print("   3. Select 'Commercial-View (Commercial Lending)' kernel")
        print("   4. Try sample code from notebooks/commercial_view_startup.ipynb")

        # Create sample notebook
        create_sample_notebook()

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install kernel: {e}")
        if kernel_dir.exists():
            shutil.rmtree(kernel_dir)
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        if kernel_dir.exists():
            shutil.rmtree(kernel_dir)
        return False


def create_sample_notebook() -> None:
    """Create a sample notebook demonstrating Commercial-View features"""
    project_root = Path(__file__).parent.parent
    notebooks_dir = project_root / "notebooks"
    notebooks_dir.mkdir(exist_ok=True)

    sample_notebook = notebooks_dir / "commercial_view_getting_started.ipynb"

    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Commercial-View Getting Started\n",
                    "\n",
                    "Welcome to Commercial-View - your commercial lending analytics platform!\n",
                    "\n",
                    "## 🏦 What You Can Do\n",
                    "- Analyze commercial loan portfolios\n",
                    "- Generate pricing models\n",
                    "- Calculate Days Past Due (DPD)\n",
                    "- Create KPI reports\n",
                    "- Assess portfolio risk",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Verify Commercial-View environment\n",
                    "import os\n",
                    "import sys\n",
                    "from pathlib import Path\n",
                    "\n",
                    'print("🏦 Commercial-View Environment Status")\n',
                    'print("=" * 40)\n',
                    "print(f\"📁 Project Root: {os.environ.get('COMMERCIAL_VIEW_ROOT', 'Not set')}\")\n",
                    "print(f\"🐍 Python Path: {os.environ.get('PYTHONPATH', 'Not set')}\")\n",
                    "print(f\"🔧 Environment: {os.environ.get('ENVIRONMENT', 'Not set')}\")\n",
                    "print(f\"🐛 Debug Mode: {os.environ.get('DEBUG', 'Not set')}\")\n",
                    "print(f\"🏦 CV Mode: {os.environ.get('COMMERCIAL_VIEW_MODE', 'Not set')}\")",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Import essential libraries\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "\n",
                    "# Configure plotting for commercial lending\n",
                    "plt.style.use('default')\n",
                    "sns.set_palette('Set2')\n",
                    "\n",
                    'print("📊 Data science libraries loaded successfully!")\n',
                    'print(f"🐼 Pandas: {pd.__version__}")\n',
                    'print(f"🔢 NumPy: {np.__version__}")',
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Load Commercial-View configurations\n",
                    "import yaml\n",
                    "\n",
                    "def load_config(config_path):\n",
                    '    """Load Commercial-View configuration file"""\n',
                    "    try:\n",
                    "        with open(config_path, 'r') as f:\n",
                    "            return yaml.safe_load(f)\n",
                    "    except FileNotFoundError:\n",
                    "        return None\n",
                    "\n",
                    "# Load configurations\n",
                    "pricing_config = load_config(os.environ.get('PRICING_CONFIG_PATH'))\n",
                    "dpd_config = load_config(os.environ.get('DPD_POLICY_PATH'))\n",
                    "column_config = load_config(os.environ.get('COLUMN_MAPS_PATH'))\n",
                    "\n",
                    'print("⚙️  Configuration Status:")\n',
                    "print(f\"   Pricing Config: {'✅ Loaded' if pricing_config else '❌ Not found'}\")\n",
                    "print(f\"   DPD Config: {'✅ Loaded' if dpd_config else '❌ Not found'}\")\n",
                    "print(f\"   Column Config: {'✅ Loaded' if column_config else '❌ Not found'}\")",
                ],
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 🚀 Next Steps\n",
                    "\n",
                    "1. **Load your commercial loan data** using `pd.read_csv()` or `pd.read_excel()`\n",
                    "2. **Apply Commercial-View processing** using the loaded configurations\n",
                    "3. **Generate insights** with built-in commercial lending analytics\n",
                    "4. **Export results** for reporting and compliance\n",
                    "\n",
                    "### 📚 Resources\n",
                    "- Configuration files: `/configs/`\n",
                    "- Sample data: `/data/`\n",
                    "- Documentation: `/docs/`\n",
                    "- Scripts: `/scripts/`",
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

    with open(sample_notebook, "w") as f:
        json.dump(notebook_content, f, indent=2)

    print(f"📓 Created sample notebook: {sample_notebook}")


def main():
    """Main installation function with enhanced error handling"""
    try:
        success = install_commercial_view_kernel()
        if success:
            print("\n🎉 Installation completed successfully!")
            print("💡 Run 'jupyter lab' to start using Commercial-View kernel")
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Installation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
=======
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
>>>>>>> 9039104 (Add missing project files and documentation)
