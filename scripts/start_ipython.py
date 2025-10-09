#!/usr/bin/env python3
"""
<<<<<<< HEAD
Enhanced IPython startup script for Commercial-View commercial lending development
=======
Enhanced IPython startup script for Commercial-View development
>>>>>>> 9039104 (Add missing project files and documentation)
"""

import os
import sys
<<<<<<< HEAD
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_commercial_view_configs() -> Dict[str, Any]:
    """Load Commercial-View configuration files"""
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
                print(f"✅ Loaded {name} configuration")
            except Exception as e:
                print(f"⚠️  Failed to load {name} config: {e}")
                configs[name] = None
        else:
            print(f"⚠️  Configuration file not found: {path}")
            configs[name] = None

    return configs


def setup_commercial_view_environment():
    """Setup Commercial-View specific environment for IPython"""

    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))
    sys.path.insert(0, str(project_root / "scripts"))

    # Set comprehensive environment variables
    env_vars = {
        "COMMERCIAL_VIEW_ROOT": str(project_root),
        "COMMERCIAL_VIEW_MODE": "ipython",
        "ENVIRONMENT": "development",
        "DEBUG": "true",
        "PRICING_CONFIG_PATH": str(project_root / "configs" / "pricing_config.yml"),
        "DPD_POLICY_PATH": str(project_root / "configs" / "dpd_policy.yml"),
        "COLUMN_MAPS_PATH": str(project_root / "configs" / "column_maps.yml"),
        "DATA_DIR": str(project_root / "data"),
        "EXPORT_DIR": str(project_root / "abaco_runtime" / "exports"),
        "PYTHONPATH": f"{project_root / 'src'}:{project_root / 'scripts'}:{os.environ.get('PYTHONPATH', '')}",
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    # Load .env files with priority
    env_files = [".env", ".env.local", ".env.development"]

    for env_file_name in env_files:
        env_file = project_root / env_file_name
        if env_file.exists():
            print(f"📝 Loading {env_file_name}")
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "=" in line:
                        try:
                            key, value = line.strip().split("=", 1)
                            # Remove quotes if present
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
                        except ValueError:
                            continue

    print("🏦 Commercial-View development environment loaded")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path includes: {project_root}/src, {project_root}/scripts")

    return project_root


def create_commercial_view_namespace() -> Dict[str, Any]:
    """Create enhanced namespace with Commercial-View modules and utilities"""

    # Standard data science imports - enhanced error handling
    user_ns = {"Path": Path, "os": os, "sys": sys, "json": json, "yaml": yaml}

    # Import standard libraries with fallbacks
    try:
        import pandas as pd
        import numpy as np

        user_ns.update({"pd": pd, "np": np})
        print("📊 Core data libraries loaded (pandas, numpy)")
    except ImportError as e:
        print(f"⚠️  Core data libraries not available: {e}")
        # Provide fallback implementations
        user_ns.update({"pd": None, "np": None})

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        user_ns.update({"plt": plt, "sns": sns})

        # Configure plotting for commercial lending
        plt.style.use("default")
        sns.set_palette("Set2")

        print("📊 Visualization libraries loaded (matplotlib, seaborn)")

    except ImportError as e:
        print(f"⚠️  Visualization libraries not available: {e}")
        user_ns.update({"plt": None, "sns": None})

    # Load Commercial-View configurations
    configs = load_commercial_view_configs()
    user_ns["configs"] = configs

    # Try to import Commercial-View modules
    commercial_modules = {}

    # Import core application modules
    try:
        from api import app

        commercial_modules["app"] = app
        print("✅ FastAPI app imported")
    except ImportError:
        try:
            from main import app

            commercial_modules["app"] = app
            print("✅ FastAPI app imported from main")
        except ImportError:
            print("⚠️  FastAPI app not available")

    try:
        from data_loader import DataLoader

        commercial_modules["DataLoader"] = DataLoader
        print("✅ DataLoader imported")
    except ImportError:
        print("⚠️  DataLoader not available")

    # Try to import commercial lending modules
    cv_modules = [
        ("pricing", "commercial_view.pricing.calculator"),
        ("dpd", "commercial_view.dpd.analyzer"),
        ("kpi", "commercial_view.kpi.generator"),
        ("risk", "commercial_view.risk.assessor"),
        ("export", "commercial_view.export.manager"),
    ]

    for module_name, module_path in cv_modules:
        try:
            module = __import__(module_path, fromlist=[""])
            commercial_modules[module_name] = module
            print(f"✅ {module_name} module imported")
        except ImportError:
            print(f"⚠️  {module_name} module not available")

    user_ns.update(commercial_modules)

    # Add enhanced utility functions
    def load_sample_data():
        """Load sample commercial lending data"""
        data_dir = Path(os.environ.get("DATA_DIR", "data"))
        sample_files = list(data_dir.glob("**/*.csv"))

        if sample_files:
            print("📊 Available sample data files:")
            for i, file in enumerate(sample_files[:5], 1):
                print(f"   {i}. {file.name}")

            if len(sample_files) > 5:
                print(f"   ... and {len(sample_files) - 5} more files")

            # Load first file if pandas is available
            if user_ns.get("pd") is not None:
                try:
                    df = user_ns["pd"].read_csv(sample_files[0])
                    print(
                        f"📈 Loaded {sample_files[0].name}: {df.shape[0]} rows, {df.shape[1]} columns"
                    )
                    return df
                except Exception as e:
                    print(f"⚠️  Error loading data: {e}")
                    return sample_files[0]
            else:
                return sample_files[0]
        else:
            print("⚠️  No sample data files found")
            return None

    def show_config():
        """Display current Commercial-View configuration"""
        print("🔧 Commercial-View Configuration:")
        for name, config in configs.items():
            if config:
                print(f"   ✅ {name}: Loaded")
                if isinstance(config, dict) and name == "figma":
                    dashboard_id = (
                        config.get("figma", {})
                        .get("commercial_view", {})
                        .get("dashboard_file_id")
                    )
                    if dashboard_id:
                        print(f"      Dashboard ID: {dashboard_id[:20]}...")
            else:
                print(f"   ❌ {name}: Not available")

    def quick_analysis():
        """Quick commercial lending portfolio analysis"""
        print("🏦 Commercial Lending Quick Analysis")
        print("Available functions:")
        print("   - load_sample_data(): Load and preview sample CSV files")
        print("   - show_config(): Display configuration status")
        if "DataLoader" in commercial_modules:
            print("   - DataLoader(): Initialize commercial lending data loader")
        if "pricing" in commercial_modules:
            print("   - pricing: Commercial loan pricing and rate models")
        if "dpd" in commercial_modules:
            print("   - dpd: Days past due analysis and delinquency tracking")
        if "kpi" in commercial_modules:
            print("   - kpi: Key performance indicator generation")
        if "risk" in commercial_modules:
            print("   - risk: Portfolio risk assessment and modeling")
        if "export" in commercial_modules:
            print("   - export: Data export and reporting utilities")

    def figma_status():
        """Check Figma integration status"""
        figma_config = configs.get("figma")
        if figma_config:
            print("🎨 Figma Integration Status:")
            dashboard_id = (
                figma_config.get("figma", {})
                .get("commercial_view", {})
                .get("dashboard_file_id")
            )
            if dashboard_id:
                print(f"   ✅ Dashboard configured: {dashboard_id[:20]}...")
            else:
                print("   ⚠️  No dashboard ID configured")
        else:
            print("❌ Figma configuration not found")

    user_ns.update(
        {
            "load_sample_data": load_sample_data,
            "show_config": show_config,
            "quick_analysis": quick_analysis,
            "figma_status": figma_status,
        }
    )

    return user_ns


def start_enhanced_ipython():
    """Start IPython with Commercial-View enhancements"""

    project_root = setup_commercial_view_environment()

    try:
        from IPython import start_ipython
        from IPython.terminal.prompts import Prompts, Token

        # Create enhanced namespace
        user_ns = create_commercial_view_namespace()

        # Enhanced IPython startup banner
        banner = f"""
🏦 Commercial-View Development Shell
📁 Project: {project_root.name}
🐍 Python: {sys.version.split()[0]}
🔧 Environment: {os.environ.get('ENVIRONMENT', 'unknown')}

📊 Pre-loaded modules:
  pd, np              - Data science core (pandas, numpy)
  plt, sns            - Visualization (matplotlib, seaborn)
  configs             - Commercial-View configurations
  app                 - FastAPI application (if available)
  DataLoader          - Data loading utilities (if available)

🏦 Commercial Lending modules:
  pricing             - Commercial loan pricing and rates
  dpd                 - Days past due analysis  
  kpi                 - KPI generation and metrics
  risk                - Risk assessment and modeling
  export              - Export and reporting tools

🚀 Quick start commands:
  quick_analysis()    - Show available analysis functions
  show_config()       - Display configuration status
  load_sample_data()  - Load and preview sample data files
  figma_status()      - Check Figma integration status
  
  %load_ext autoreload
  %autoreload 2       - Auto-reload modules on change
        """

        # Custom prompt for Commercial-View
        class CommercialViewPrompts(Prompts):
            def in_prompt_tokens(self, cli=None):
                return [
                    (Token.Prompt, "🏦 CV"),
                    (Token.Prompt, "["),
                    (Token.PromptNum, str(self.shell.execution_count)),
                    (Token.Prompt, "]: "),
                ]

        # IPython configuration with auto-reload
        config = {
            "InteractiveShellApp": {
                "exec_lines": [
                    "%load_ext autoreload",
                    "%autoreload 2",
                    'print("🔄 Auto-reload enabled for Commercial-View development")',
                ]
            },
            "TerminalIPythonApp": {
                "display_banner": True,
            },
        }

        print("🚀 Starting Commercial-View IPython shell...")

        start_ipython(
            argv=[], user_ns=user_ns, display_banner=True, banner2=banner, config=config
        )

    except ImportError:
        print("❌ IPython not installed. Install with: pip install ipython")
        print(
            "💡 For full development environment: pip install ipython pandas numpy matplotlib seaborn"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Commercial-View IPython session ended")
        sys.exit(0)


def main():
    """Main function with enhanced command line options"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--config":
            setup_commercial_view_environment()
            configs = load_commercial_view_configs()
            print("\n🔧 Configuration Status:")
            for name, config in configs.items():
                status = "✅ Loaded" if config else "❌ Missing"
                print(f"   {name}: {status}")

        elif command == "--check":
            setup_commercial_view_environment()
            user_ns = create_commercial_view_namespace()
            available_modules = len(
                [
                    k
                    for k, v in user_ns.items()
                    if v is not None and not k.startswith("_")
                ]
            )
            print(f"\n📦 Available modules and functions: {available_modules}")

        elif command == "--figma":
            setup_commercial_view_environment()
            configs = load_commercial_view_configs()
            figma_config = configs.get("figma")
            if figma_config:
                print("🎨 Figma Configuration:")
                print(json.dumps(figma_config, indent=2))
            else:
                print("❌ Figma configuration not found")

        elif command == "--help":
            print("🏦 Commercial-View IPython Startup")
            print("Options:")
            print("  --config  Show configuration status")
            print("  --check   Check available modules and functions")
            print("  --figma   Show Figma integration configuration")
            print("  --help    Show this help message")

        else:
            print("🏦 Commercial-View IPython Startup")
            print("Unknown option. Use --help for available commands.")
    else:
        start_enhanced_ipython()


if __name__ == "__main__":
    main()
=======
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
>>>>>>> 9039104 (Add missing project files and documentation)
