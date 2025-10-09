#!/usr/bin/env python3
"""
<<<<<<< HEAD
Enhanced Jupyter startup script for Commercial-View commercial lending development
=======
Enhanced Jupyter startup script for Commercial-View development
>>>>>>> 9039104 (Add missing project files and documentation)
"""

import os
import sys
<<<<<<< HEAD
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def load_commercial_view_configs() -> Dict:
    """Load Commercial-View configuration files for Jupyter integration"""
    project_root = Path(
        os.environ.get("COMMERCIAL_VIEW_ROOT", Path(__file__).parent.parent)
    )
    configs = {}

    config_files = {
        "pricing": project_root / "configs" / "pricing_config.yml",
        "dpd": project_root / "configs" / "dpd_policy.yml",
        "columns": project_root / "configs" / "column_maps.yml",
        "figma": project_root / "configs" / "figma_config.json",
    }

    for name, path in config_files.items():
        if path.exists():
            try:
                if path.suffix == ".json":
                    with open(path, "r") as f:
                        configs[name] = json.load(f)
                else:
                    with open(path, "r") as f:
                        configs[name] = yaml.safe_load(f)
                print(f"✅ Loaded {name} configuration for Jupyter")
            except Exception as e:
                print(f"⚠️  Failed to load {name} config: {e}")
                configs[name] = None

    return configs

=======
import subprocess
from pathlib import Path
>>>>>>> 9039104 (Add missing project files and documentation)

def setup_jupyter_environment():
    """Setup Commercial-View environment for Jupyter"""
    project_root = Path(__file__).parent.parent
<<<<<<< HEAD

    # Set comprehensive environment variables
    env_vars = {
        "COMMERCIAL_VIEW_ROOT": str(project_root),
        "COMMERCIAL_VIEW_MODE": "jupyter",
        "ENVIRONMENT": "development",
        "DEBUG": "true",
        "PRICING_CONFIG_PATH": str(project_root / "configs" / "pricing_config.yml"),
        "DPD_POLICY_PATH": str(project_root / "configs" / "dpd_policy.yml"),
        "COLUMN_MAPS_PATH": str(project_root / "configs" / "column_maps.yml"),
        "DATA_DIR": str(project_root / "data"),
        "EXPORT_DIR": str(project_root / "abaco_runtime" / "exports"),
        "PYTHONPATH": f"{project_root}/src:{project_root}/scripts:{os.environ.get('PYTHONPATH', '')}",
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    # Load multiple .env files with priority
    env_files = [".env", ".env.local", ".env.development"]

    for env_file_name in env_files:
        env_file = project_root / env_file_name
        if env_file.exists():
            print(f"📝 Loading {env_file_name} for Jupyter")
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "=" in line:
                        try:
                            key, value = line.strip().split("=", 1)
                            # Remove quotes if present
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
                        except ValueError:
                            continue

    # Load Commercial-View configurations
    configs = load_commercial_view_configs()

    print("🏦 Commercial-View Jupyter environment configured")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path includes: {project_root}/src, {project_root}/scripts")

    return configs


def create_jupyter_config() -> Path:
    """Create Jupyter configuration optimized for Commercial-View"""
    project_root = Path(os.environ["COMMERCIAL_VIEW_ROOT"])
    jupyter_config_dir = project_root / ".jupyter"
    jupyter_config_dir.mkdir(exist_ok=True)

    config_content = '''# Commercial-View Jupyter Configuration
c = get_config()

# Server Configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.notebook_dir = '.'

# Security
c.ServerApp.token = ''  # Use empty token for development
c.ServerApp.password = ''
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True

# Commercial-View specific settings
c.ServerApp.extra_static_paths = ['./frontend/dashboard/build/static']
c.ServerApp.extra_template_paths = ['./templates']

# Kernel settings for Commercial-View
c.MappingKernelManager.default_kernel_name = 'commercial-view'

# File save hooks for commercial lending data
def commercial_view_pre_save_hook(model, path, contents_manager):
    """Pre-save hook for Commercial-View notebooks"""
    if model['type'] == 'notebook':
        # Add Commercial-View metadata
        if 'metadata' not in model['content']:
            model['content']['metadata'] = {}
        
        model['content']['metadata']['commercial_view'] = {
            'platform': 'commercial_lending',
            'last_modified': str(datetime.now()),
            'environment': 'development'
        }

c.FileContentsManager.pre_save_hook = commercial_view_pre_save_hook
'''

    config_file = jupyter_config_dir / "jupyter_lab_config.py"
    with open(config_file, "w") as f:
        f.write(config_content)

    print(f"📄 Created Jupyter config: {config_file}")
    return config_file


def create_startup_notebooks() -> List[Path]:
    """Create Commercial-View startup notebooks"""
    notebooks_dir = Path("notebooks")
    notebooks_dir.mkdir(exist_ok=True)

    # Commercial-View Getting Started notebook
    getting_started_notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Commercial-View Commercial Lending Analytics\n",
                    "\n",
                    "Welcome to Commercial-View Jupyter Lab environment for commercial lending analytics.\n",
                    "\n",
                    "## 🏦 Available Features\n",
                    "- Commercial loan pricing models\n",
                    "- Days Past Due (DPD) analysis\n",
                    "- KPI generation and reporting\n",
                    "- Portfolio risk assessment\n",
                    "- Data export and visualization\n",
                    "\n",
                    "## 🚀 Quick Start\n",
                    "Run the cells below to set up your Commercial-View environment.",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Import Commercial-View environment\n",
                    "import os\n",
                    "import sys\n",
                    "from pathlib import Path\n",
                    "\n",
                    "# Verify Commercial-View setup\n",
                    'print("🏦 Commercial-View Environment Status")\n',
                    'print("=" * 40)\n',
                    "print(f\"📁 Project Root: {os.environ.get('COMMERCIAL_VIEW_ROOT', 'Not set')}\")\n",
                    "print(f\"🔧 Environment: {os.environ.get('ENVIRONMENT', 'Not set')}\")\n",
                    "print(f\"🏦 CV Mode: {os.environ.get('COMMERCIAL_VIEW_MODE', 'Not set')}\")\n",
                    "print(f\"📊 Data Directory: {os.environ.get('DATA_DIR', 'Not set')}\")\n",
                    "print(f\"📤 Export Directory: {os.environ.get('EXPORT_DIR', 'Not set')}\")",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Import essential libraries for commercial lending\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "from datetime import datetime, timedelta\n",
                    "\n",
                    "# Configure visualization for commercial lending\n",
                    "plt.style.use('default')\n",
                    "sns.set_palette('Set2')\n",
                    "plt.rcParams['figure.figsize'] = (12, 8)\n",
                    "\n",
                    'print("📊 Data science libraries loaded for commercial lending")\n',
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
                    "import json\n",
                    "\n",
                    "def load_config(config_path):\n",
                    '    """Load Commercial-View configuration file"""\n',
                    "    try:\n",
                    "        with open(config_path, 'r') as f:\n",
                    "            if config_path.endswith('.json'):\n",
                    "                return json.load(f)\n",
                    "            else:\n",
                    "                return yaml.safe_load(f)\n",
                    "    except FileNotFoundError:\n",
                    "        return None\n",
                    "\n",
                    "# Load all configurations\n",
                    "configs = {\n",
                    "    'pricing': load_config(os.environ.get('PRICING_CONFIG_PATH')),\n",
                    "    'dpd': load_config(os.environ.get('DPD_POLICY_PATH')),\n",
                    "    'columns': load_config(os.environ.get('COLUMN_MAPS_PATH'))\n",
                    "}\n",
                    "\n",
                    'print("⚙️  Configuration Status:")\n',
                    "for name, config in configs.items():\n",
                    '    status = "✅ Loaded" if config else "❌ Not found"\n',
                    '    print(f"   {name.title()}: {status}")',
                ],
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 📊 Sample Commercial Lending Analysis\n",
                    "\n",
                    "The cells below demonstrate basic commercial lending analytics using Commercial-View.",
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
            "commercial_view": {
                "platform": "commercial_lending",
                "notebook_type": "getting_started",
                "created": str(datetime.now()),
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    getting_started_file = notebooks_dir / "commercial_view_getting_started.ipynb"
    with open(getting_started_file, "w") as f:
        json.dump(getting_started_notebook, f, indent=2)

    print(f"📓 Created getting started notebook: {getting_started_file}")

    return [getting_started_file]


def check_jupyter_installation() -> bool:
    """Check if Jupyter Lab is installed and available"""
    try:
        result = subprocess.run(
            ["jupyter", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ Jupyter available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Jupyter not properly installed")
            return False
    except FileNotFoundError:
        print("❌ Jupyter not found")
        return False


def install_jupyter_extensions() -> None:
    """Install useful Jupyter extensions for Commercial-View"""
    extensions = [
        "jupyterlab-git",
        "@jupyter-widgets/jupyterlab-manager",
        "jupyterlab_code_formatter",
    ]

    print("🔧 Installing Jupyter Lab extensions...")
    for extension in extensions:
        try:
            subprocess.run(
                ["jupyter", "labextension", "install", extension],
                capture_output=True,
                check=True,
            )
            print(f"✅ Installed extension: {extension}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install extension: {extension}")


def start_jupyter_lab():
    """Start Jupyter Lab with Commercial-View configuration"""
    # Setup environment and configurations
    configs = setup_jupyter_environment()

    # Check installation
    if not check_jupyter_installation():
        print("💡 Install Jupyter Lab: pip install jupyterlab")
        return

    # Create Jupyter configuration
    config_file = create_jupyter_config()

    # Create startup notebooks
    startup_notebooks = create_startup_notebooks()

    # Install extensions (optional)
    try:
        install_jupyter_extensions()
    except Exception as e:
        print(f"⚠️  Extension installation failed: {e}")

    try:
        # Enhanced Jupyter Lab command
        cmd = [
            "jupyter",
            "lab",
            "--notebook-dir",
            ".",
            "--ip",
            "0.0.0.0",
            "--port",
            "8888",
            "--no-browser",
            "--allow-root",
            "--config",
            str(config_file),
        ]

        print("🔬 Starting Jupyter Lab for Commercial-View...")
        print("🏦 Commercial lending analytics environment ready")
        print(f"📊 Available configurations: {len([c for c in configs.values() if c])}")
        print(f"📓 Startup notebooks: {len(startup_notebooks)}")
        print("🌐 Access Jupyter Lab at: http://localhost:8888")
        print("💡 Open 'commercial_view_getting_started.ipynb' to begin")

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n🛑 Commercial-View Jupyter Lab stopped")
    except FileNotFoundError:
        print("❌ Jupyter Lab not installed. Install with: pip install jupyterlab")
    except Exception as e:
        print(f"❌ Error starting Jupyter Lab: {e}")


def main():
    """Main function with command line options"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--check":
            setup_jupyter_environment()
            check_jupyter_installation()
        elif command == "--config":
            setup_jupyter_environment()
            create_jupyter_config()
            print("✅ Jupyter configuration created")
        elif command == "--notebooks":
            setup_jupyter_environment()
            notebooks = create_startup_notebooks()
            print(f"✅ Created {len(notebooks)} startup notebooks")
        elif command == "--help":
            print("🏦 Commercial-View Jupyter Lab Startup")
            print("Options:")
            print("  --check     Check Jupyter installation")
            print("  --config    Create Jupyter configuration only")
            print("  --notebooks Create startup notebooks only")
            print("  --help      Show this help message")
        else:
            print("🏦 Commercial-View Jupyter Lab Startup")
            print("Unknown option. Use --help for available commands.")
    else:
        start_jupyter_lab()


if __name__ == "__main__":
    main()
=======
    
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
>>>>>>> 9039104 (Add missing project files and documentation)
