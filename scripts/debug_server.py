#!/usr/bin/env python3
"""
Enhanced debug server script for Commercial-View commercial lending platform with remote debugging support
"""

import debugpy
import sys
import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any


def setup_commercial_view_environment() -> Dict[str, Any]:
    """Setup Commercial-View specific debugging environment"""
    project_root = Path(__file__).parent.parent

    # Commercial lending specific environment variables
    env_config = {
        "DEBUG": "true",
        "ENVIRONMENT": "development",
        "COMMERCIAL_VIEW_ROOT": str(project_root),
        "COMMERCIAL_VIEW_MODE": "debug",
        "PRICING_CONFIG_PATH": str(project_root / "configs" / "pricing_config.yml"),
        "DPD_POLICY_PATH": str(project_root / "configs" / "dpd_policy.yml"),
        "COLUMN_MAPS_PATH": str(project_root / "configs" / "column_maps.yml"),
        "LOG_LEVEL": "DEBUG",
        "API_BASE_URL": "http://localhost:8000",
        "ENABLE_PROFILING": "true",
        "ENABLE_STACK_TRACES": "true",
    }

    # Set environment variables
    for key, value in env_config.items():
        os.environ[key] = value

    # Add project paths to Python path
    sys.path.insert(0, str(project_root / "src"))
    sys.path.insert(0, str(project_root / "scripts"))

    print("🏦 Commercial-View environment configured")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python paths: {len(sys.path)} entries")

    return env_config


def setup_debug_logging() -> logging.Logger:
    """Setup comprehensive debug logging for commercial lending operations"""
    log_dir = Path("var/log")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "debug.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Create specialized loggers for commercial lending components
    loggers = {
        "pricing": logging.getLogger("commercial_view.pricing"),
        "dpd": logging.getLogger("commercial_view.dpd"),
        "kpi": logging.getLogger("commercial_view.kpi"),
        "risk": logging.getLogger("commercial_view.risk"),
        "export": logging.getLogger("commercial_view.export"),
    }

    for name, logger in loggers.items():
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(log_dir / f"{name}_debug.log")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)

    main_logger = logging.getLogger("debug_server")
    main_logger.info("🔍 Debug logging configured for Commercial-View")

    return main_logger


def validate_debug_prerequisites() -> bool:
    """Validate that all prerequisites for debugging are met"""
    logger = logging.getLogger("debug_server")

    # Check critical files
    critical_files = [
        "run.py",
        "src/main.py",
        "configs/pricing_config.yml",
        "configs/dpd_policy.yml",
        "configs/column_maps.yml",
    ]

    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        logger.error(f"❌ Missing critical files: {missing_files}")
        return False

    # Check if debugpy is available
    try:
        import debugpy

        logger.info("✅ debugpy module available")
    except ImportError:
        logger.error("❌ debugpy not installed. Run: pip install debugpy")
        return False

    # Check if Commercial-View modules can be imported
    try:
        sys.path.insert(0, "src")
        # Test import without actually importing to avoid side effects
        import importlib.util

        spec = importlib.util.find_spec("main")
        if spec is None:
            logger.error("❌ Cannot find main module")
            return False
        logger.info("✅ Main module can be imported")
    except Exception as e:
        logger.error(f"❌ Module import test failed: {e}")
        return False

    logger.info("✅ All debug prerequisites validated")
    return True


def start_debug_server(
    port: int = 5678,
    wait_for_client: bool = True,
    api_port: int = 8000,
    enable_profiling: bool = False,
) -> None:
    """Start the Commercial-View API server with enhanced debugging capabilities"""

    logger = setup_debug_logging()
    logger.info(f"🐛 Starting Commercial-View debug server on port {port}")

    # Validate prerequisites
    if not validate_debug_prerequisites():
        logger.error("❌ Debug prerequisites validation failed")
        sys.exit(1)

    # Setup environment
    env_config = setup_commercial_view_environment()

    # Configure debugpy with enhanced settings
    try:
        debugpy.configure(
            python=sys.executable,
            justMyCode=False,  # Enable debugging of library code
            redirectOutput=True,  # Redirect stdout/stderr to debug console
            showReturnValue=True,  # Show return values in debugger
        )

        debugpy.listen(("0.0.0.0", port))
        logger.info(f"🔍 Debug server listening on 0.0.0.0:{port}")

        if wait_for_client:
            logger.info(f"⏳ Waiting for debugger to attach on port {port}...")
            print(f"💡 Connect your debugger to localhost:{port}")
            print(f"💡 VS Code: Add debug configuration with port {port}")
            debugpy.wait_for_client()
            logger.info("🔗 Debugger attached successfully!")
        else:
            logger.info("🚀 Starting without waiting for debugger")

    except Exception as e:
        logger.error(f"❌ Failed to setup debugpy: {e}")
        sys.exit(1)

    # Setup profiling if enabled
    profiler = None
    if enable_profiling:
        try:
            import cProfile

            profiler = cProfile.Profile()
            profiler.enable()
            logger.info("📊 Profiling enabled")
        except ImportError:
            logger.warning("⚠️  Profiling requested but cProfile not available")

    # Import and configure the application
    try:
        # Set breakpoint for initial debugging
        if wait_for_client:
            debugpy.breakpoint()

        logger.info("📦 Importing Commercial-View application...")

        # Import application components
        from run import app
        import uvicorn

        # Configure uvicorn for debugging
        uvicorn_config = {
            "app": app,
            "host": "0.0.0.0",
            "port": api_port,
            "reload": False,  # Disable reload in debug mode
            "log_level": "debug",
            "access_log": True,
            "use_colors": True,
            "debug": True,
        }

        logger.info(f"🚀 Starting Commercial-View API server on port {api_port}")
        logger.info("🏦 Commercial lending features available for debugging:")
        logger.info("   - /api/v1/pricing - Commercial loan pricing")
        logger.info("   - /api/v1/dpd-analysis - Days past due analysis")
        logger.info("   - /api/v1/kpi - KPI generation")
        logger.info("   - /api/v1/risk-assessment - Risk analysis")
        logger.info("   - /api/v1/export - Data export management")

        # Start the server
        uvicorn.run(**uvicorn_config)

    except ImportError as e:
        logger.error(f"❌ Failed to import application: {e}")
        logger.error(
            "💡 Ensure all dependencies are installed: pip install -r requirements.txt"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Debug server stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise
    finally:
        # Save profiling results if enabled
        if profiler:
            profile_dir = Path("var/profiling")
            profile_dir.mkdir(parents=True, exist_ok=True)
            profile_file = (
                profile_dir
                / f"debug_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pro"
            )
            profiler.dump_stats(str(profile_file))
            logger.info(f"📊 Profiling results saved to: {profile_file}")


def create_debug_configuration() -> Dict[str, Any]:
    """Create VS Code debug configuration for Commercial-View"""
    debug_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Commercial-View Debug Server",
                "type": "python",
                "request": "attach",
                "connect": {"host": "localhost", "port": 5678},
                "pathMappings": [
                    {"localRoot": "${workspaceFolder}", "remoteRoot": "."}
                ],
                "justMyCode": False,
                "redirectOutput": True,
                "showReturnValue": True,
            },
            {
                "name": "Commercial-View Local Debug",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/scripts/debug_server.py",
                "args": ["--no-wait"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"DEBUG": "true", "ENVIRONMENT": "development"},
            },
        ],
    }

    # Save to .vscode directory
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    config_file = vscode_dir / "launch.json"
    with open(config_file, "w") as f:
        json.dump(debug_config, f, indent=2)

    print(f"📝 VS Code debug configuration saved to: {config_file}")
    return debug_config


def main():
    """Enhanced main function with comprehensive commercial lending debug options"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced debug server for Commercial-View commercial lending platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start with default settings
  %(prog)s --no-wait --port 5679    # Start without waiting, custom port
  %(prog)s --profile --api-port 8001 # Enable profiling, custom API port
  %(prog)s --create-config          # Create VS Code debug configuration
        """,
    )

    parser.add_argument(
        "--port", type=int, default=5678, help="Debug port (default: 5678)"
    )
    parser.add_argument(
        "--api-port", type=int, default=8000, help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--no-wait", action="store_true", help="Don't wait for debugger to attach"
    )
    parser.add_argument(
        "--profile", action="store_true", help="Enable performance profiling"
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create VS Code debug configuration and exit",
    )

    args = parser.parse_args()

    if args.create_config:
        create_debug_configuration()
        print("✅ VS Code debug configuration created")
        print("💡 Open VS Code and use 'Commercial-View Debug Server' configuration")
        return

    try:
        start_debug_server(
            port=args.port,
            wait_for_client=not args.no_wait,
            api_port=args.api_port,
            enable_profiling=args.profile,
        )
    except KeyboardInterrupt:
        print("\n🛑 Debug server interrupted")
    except Exception as e:
        print(f"\n❌ Debug server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
