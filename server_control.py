#!/usr/bin/env python3
"""
Server control utility for the Commercial View API.

This script provides command-line controls for:
- Starting the API server with configurable port
- Auto-reloading on code changes
- Killing existing processes on the specified port
- Configuring logging level
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from typing import List, Optional, Tuple


def find_port_processes(port: int) -> List[int]:
    """Find PIDs of processes using the specified port."""
    pids = []
    try:
        # Check for processes using the port
        output = subprocess.check_output(
            ["lsof", "-i", f":{port}", "-t"], 
            stderr=subprocess.STDOUT,
            universal_newlines=True
        ).strip()
        if output:
            pids = [int(pid) for pid in output.split('\n') if pid.strip()]
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
            print(f"Killed process {pid}" + (" (forced)" if force else ""))
        except ProcessLookupError:
            pass  # Process already gone
        except PermissionError:
            print(f"Permission denied when trying to kill PID {pid}")
            success = False
        except Exception as e:
            print(f"Error killing process {pid}: {str(e)}")
            success = False
    
    return success


def run_uvicorn(
    app: str = "run:app", 
    host: str = "0.0.0.0", 
    port: int = 8000,
    reload: bool = True,
    log_level: str = "info"
) -> int:
    """Run the uvicorn server with the specified parameters."""
    cmd = [
        "uvicorn", 
        app,
        "--host", host,
        "--port", str(port),
        "--log-level", log_level
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"Starting server: {' '.join(cmd)}")
    
    try:
        process = subprocess.run(cmd)
        return process.returncode
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        return 1


def check_environment() -> Tuple[bool, str]:
    """Check if the Python environment is properly set up."""
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    # Check if required packages are installed
    try:
        import uvicorn
        import fastapi
        packages_installed = True
    except ImportError:
        packages_installed = False
    
    if not in_venv:
        return False, "Not running in a virtual environment"
    if not packages_installed:
        return False, "Required packages not installed"
        
    return True, "Environment looks good"


def main() -> int:
    """Main entry point for the server control script."""
    parser = argparse.ArgumentParser(
        description="Control the Commercial View API server",
        epilog="""
Examples:
  # Start server on default port 8000
  python server_control.py
  
  # Kill existing process and start on port 8001
  python server_control.py --port 8001 --kill-existing
  
  # Just check if a port is in use
  python server_control.py --check-only --port 8000
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="Host interface to bind (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--app", 
        type=str, 
        default="run:app",
        help="Application import path (default: run:app)"
    )
    
    parser.add_argument(
        "--no-reload", 
        action="store_true",
        help="Disable auto-reload"
    )
    
    parser.add_argument(
        "--kill-existing", 
        action="store_true",
        help="Kill existing processes using the port"
    )
    
    parser.add_argument(
        "--force-kill", 
        action="store_true",
        help="Force kill processes using SIGKILL"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Log level (default: info)"
    )
    
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for processes using the port, don't start the server"
    )
    
    args = parser.parse_args()
    
    # Check environment
    env_ok, env_msg = check_environment()
    if not env_ok:
        print(f"Environment issue: {env_msg}")
        print("Tip: Activate your virtual environment with 'source .venv/bin/activate'")
        return 1
    
    # Check for existing processes
    port_pids = find_port_processes(args.port)
    
    if port_pids:
        print(f"Found {len(port_pids)} process(es) using port {args.port}:")
        for pid in port_pids:
            try:
                cmd = subprocess.check_output(
                    ["ps", "-o", "command=", "-p", str(pid)],
                    universal_newlines=True
                ).strip()
                print(f"  PID {pid}: {cmd}")
            except subprocess.CalledProcessError:
                print(f"  PID {pid}: (process info unavailable)")
        
        if args.check_only:
            return 0
            
        if args.kill_existing:
            success = kill_processes(port_pids, args.force_kill)
            if not success:
                print(f"Could not kill all processes on port {args.port}")
                return 1
                
            # Wait a moment for the port to be freed
            time.sleep(0.5)
        else:
            alt_port = args.port + 1
            print(f"Port {args.port} is in use. Try a different port:")
            print(f"  {sys.argv[0]} --port {alt_port}")
            print(f"Or kill the existing process(es):")
            print(f"  {sys.argv[0]} --port {args.port} --kill-existing")
            return 1
    elif args.check_only:
        print(f"No processes found using port {args.port}")
        return 0
    
    # Run the server
    return run_uvicorn(
        app=args.app,
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    sys.exit(main())
