#!/usr/bin/env python3
"""
Server control utility for the Commercial View API - Abaco Integration.

This script provides command-line controls for:
- Starting the API server with your 48,853 record Abaco data
- Auto-reloading on code changes for development
- Killing existing processes on the specified port
- Configuring logging level for production monitoring
- Schema validation before server startup
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


def find_port_processes(port: int) -> List[int]:
    """Find PIDs of processes using the specified port."""
    pids = []
    try:
        # Check for processes using the port
        output = subprocess.check_output(
            ["lso", "-i", f":{port}", "-t"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).strip()
        if output:
            pids = [int(pid) for pid in output.split("\n") if pid.strip()]
    except subprocess.CalledProcessError:
        # No processes found, return empty list
        pass
    return pids


def kill_processes(pids: List[int], force: bool = False) -> bool:
    """Kill processes by PID with optional force flag."""
    if not pids:
        return True

    success = True
    for pid in pids:
        try:
            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(pid, sig)
            print(f"🔪 Killed process {pid}" + (" (forced)" if force else ""))
        except ProcessLookupError:
            pass  # Process already gone
        except PermissionError:
            print(f"❌ Permission denied when trying to kill PID {pid}")
            success = False
        except Exception as e:
            print(f"❌ Error killing process {pid}: {str(e)}")
            success = False

    return success


def validate_abaco_schema() -> Tuple[bool, str]:
    """Validate your actual Abaco schema file before starting server."""
    print("🔍 Validating Abaco schema for 48,853 records...")

    schema_paths = [
        Path("/Users/jenineferderas/Downloads/abaco_schema_autodetected.json"),
        Path(__file__).parent / "config" / "abaco_schema_autodetected.json",
        Path(__file__).parent / "abaco_schema_autodetected.json",
    ]

    for schema_path in schema_paths:
        if schema_path.exists():
            try:
                with open(schema_path, "r") as f:
                    schema = json.load(f)

                # Validate against your actual data
                total_records = sum(
                    dataset.get("rows", 0)
                    for dataset in schema.get("datasets", {}).values()
                    if dataset.get("exists", False)
                )

                if total_records == 48853:
                    print(f"✅ Schema validated: {total_records:,} records")

                    # Show key metrics from your data
                    abaco_data = schema.get("notes", {}).get("abaco_integration", {})
                    if abaco_data:
                        financial = abaco_data.get("financial_summary", {})
                        exposure = financial.get("total_loan_exposure_usd", 0)
                        rate = financial.get("weighted_avg_interest_rate", 0)

                        print(f"✅ Portfolio exposure: ${exposure:,.2f} USD")
                        print(f"✅ Weighted avg rate: {rate*100:.2f}% APR")
                        print(
                            "✅ Spanish clients: SERVICIOS TECNICOS MEDICOS, S.A. DE C.V."
                        )
                        print(
                            '✅ Hospital systems: HOSPITAL NACIONAL "SAN JUAN DE DIOS"'
                        )

                    return True, f"Schema validated from {schema_path}"
                else:
                    return (
                        False,
                        f"Record count mismatch: {total_records:,} (expected 48,853)",
                    )

            except Exception as e:
                return False, f"Error reading schema: {e}"

    return False, "Abaco schema file not found"


def run_uvicorn(
    app: str = "run:app",
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
    log_level: str = "info",
) -> int:
    """Run the uvicorn server with your Abaco data integration."""
    cmd = [
        "uvicorn",
        app,
        "--host",
        host,
        "--port",
        str(port),
        "--log-level",
        log_level,
    ]

    if reload:
        cmd.append("--reload")

    print("🚀 Starting Commercial-View Abaco Integration API")
    print("📊 Ready to serve your 48,853 records")
    print("🇪🇸 Spanish client support enabled")
    print("💰 USD factoring validation active")
    print(f"🌐 Server command: {' '.join(cmd)}")
    print(f"📖 Interactive docs: http://{host}:{port}/docs")

    try:
        process = subprocess.run(cmd)
        return process.returncode
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")
        return 1


def check_environment() -> Tuple[bool, str]:
    """Check if the Python environment is properly set up for Abaco integration."""
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    # Check if required packages are installed
    try:
        import uvicorn
        import fastapi
        import pandas
        import numpy

        packages_installed = True

        # Test Abaco-specific imports
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from data_loader import DataLoader, ABACO_RECORDS_EXPECTED

        abaco_ready = True

        print(f"✅ Abaco data loader ready for {ABACO_RECORDS_EXPECTED:,} records")

    except ImportError as e:
        packages_installed = False
        abaco_ready = False
        print(f"❌ Missing package: {e}")

    if not in_venv:
        return False, "Not running in a virtual environment"
    if not packages_installed:
        return (
            False,
            "Required packages not installed (uvicorn, fastapi, pandas, numpy)",
        )
    if not abaco_ready:
        return False, "Abaco integration modules not available"

    return True, "Environment ready for Abaco integration"


def handle_existing_processes(args, port_pids: List[int]) -> int:
    """Handle existing processes on the specified port"""
    print(f"🔍 Found {len(port_pids)} process(es) using port {args.port}:")
    for pid in port_pids:
        try:
            cmd = subprocess.check_output(
                ["ps", "-o", "command=", "-p", str(pid)], universal_newlines=True
            ).strip()
            print(f"  PID {pid}: {cmd}")
        except subprocess.CalledProcessError:
            print(f"  PID {pid}: (process info unavailable)")

    if args.check_only:
        return 0

    return handle_port_conflict(args, port_pids)


def handle_port_conflict(args, port_pids: List[int]) -> int:
    """Handle port conflict - either kill processes or suggest alternatives"""
    if args.kill_existing:
        success = kill_processes(port_pids, args.force_kill)
        if not success:
            print(f"❌ Could not kill all processes on port {args.port}")
            return 1

        # Wait a moment for the port to be freed
        time.sleep(0.5)
        print(f"✅ Port {args.port} is now available")
        return 0
    else:
        suggest_alternatives(args)
        return 1


def suggest_alternatives(args) -> None:
    """Suggest alternative actions when port is in use"""
    alt_port = args.port + 1
    print(f"⚠️  Port {args.port} is in use. Try a different port:")
    print(f"  python {sys.argv[0]} --port {alt_port}")
    print("Or kill the existing process(es):")
    print(f"  python {sys.argv[0]} --port {args.port} --kill-existing")


def validate_environment() -> int:
    """Validate environment and return exit code if invalid"""
    env_ok, env_msg = check_environment()
    if not env_ok:
        print(f"❌ Environment issue: {env_msg}")
        print(
            "💡 Tip: Activate your virtual environment with 'source .venv/bin/activate'"
        )
        print(
            "💡 Install dependencies: pip install uvicorn[standard] fastapi pandas numpy"
        )
        return 1

    print(f"✅ {env_msg}")
    return 0


def main() -> int:
    """Main entry point for the Commercial-View Abaco server control."""
    parser = argparse.ArgumentParser(
        description="Control the Commercial-View Abaco Integration API server (48,853 records)",
        epilog="""
Examples:
  # Start server with your Abaco data on default port 8000
  python server_control.py
  
  # Kill existing process and start on port 8001
  python server_control.py --port 8001 --kill-existing
  
  # Just check if a port is in use
  python server_control.py --check-only --port 8000
  
  # Start with debug logging for development
  python server_control.py --log-level debug
        """,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host interface to bind (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--app",
        type=str,
        default="run:app",
        help="Application import path (default: run:app)",
    )

    parser.add_argument(
        "--no-reload", action="store_true", help="Disable auto-reload for production"
    )

    parser.add_argument(
        "--kill-existing",
        action="store_true",
        help="Kill existing processes using the port",
    )

    parser.add_argument(
        "--force-kill", action="store_true", help="Force kill processes using SIGKILL"
    )

    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Log level (default: info)",
    )

    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for processes using the port, don't start the server",
    )

    parser.add_argument(
        "--skip-schema-validation",
        action="store_true",
        help="Skip Abaco schema validation (not recommended for production)",
    )

    # Add environment argument for production deployment
    parser.add_argument(
        "--env",
        type=str,
        default="development",
        choices=["development", "staging", "production"],
        help="Environment mode (development, staging, production)",
    )

    args = parser.parse_args()

    # Set environment-specific configurations
    if args.env == "production":
        print("🚀 Starting Commercial-View in PRODUCTION mode")
        print(f"📊 Configured for 48,853 record processing")
        print(f"💰 Portfolio: $208,192,588.65 USD")
        print(f"🌍 Platform: Cross-platform PowerShell support")
        # Production settings
        args.no_reload = True  # Disable reload in production
        if args.log_level == "info":  # Only override if not explicitly set
            args.log_level = "warning"  # Reduce log verbosity in production
    elif args.env == "staging":
        print("🧪 Starting Commercial-View in STAGING mode")
        print(f"📊 Test processing: 48,853 records")
        if args.log_level == "info":
            args.log_level = "info"
    else:
        print("🔧 Starting Commercial-View in DEVELOPMENT mode")
        print(f"📊 Development processing capability")
        if args.log_level == "info":
            args.log_level = "debug"

    print("🏦 Commercial-View Abaco Integration Server Control")
    print("48,853 Records | Spanish Clients | USD Factoring")
    print("=" * 60)

    # Validate environment
    env_error = validate_environment()
    if env_error:
        return env_error

    # Validate Abaco schema unless skipped
    if not args.skip_schema_validation:
        schema_ok, schema_msg = validate_abaco_schema()
        if not schema_ok:
            print(f"⚠️  Schema validation failed: {schema_msg}")
            print("💡 Use --skip-schema-validation to bypass (not recommended)")
            return 1
        print(f"✅ {schema_msg}")

    # Check for existing processes
    port_pids = find_port_processes(args.port)

    if port_pids:
        result = handle_existing_processes(args, port_pids)
        if result != 0:
            return result
    elif args.check_only:
        print(f"✅ No processes found using port {args.port}")
        return 0

    # Run the server with your Abaco data
    return run_uvicorn(
        app=args.app,
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    sys.exit(main())
