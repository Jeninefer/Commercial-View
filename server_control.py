"""
Server control utility for Commercial View.

This script helps manage the FastAPI server, find and kill conflicting processes,
and start the server with a configurable port.
"""

import os
import sys
import subprocess
import argparse
from typing import Optional, List, Tuple

def check_port_in_use(port: int) -> Tuple[bool, Optional[int]]:
    """Check if a port is in use and return the PID if found."""
    try:
        # Use lsof to find processes using the port
        result = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return False, None
            
        # Parse the output to get the PID
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:  # Header + at least one process
            process_info = lines[1].split()
            if len(process_info) > 1:
                try:
                    return True, int(process_info[1])
                except (IndexError, ValueError):
                    pass
                    
        return True, None
        
    except Exception as e:
        print(f"Error checking port: {str(e)}")
        return False, None

def kill_process(pid: int) -> bool:
    """Kill a process by PID."""
    try:
        subprocess.run(["kill", "-9", str(pid)], check=True)
        print(f"Successfully killed process {pid}")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to kill process {pid}")
        return False

def start_server(port: int = 8000, reload: bool = True) -> None:
    """Start the FastAPI server with uvicorn."""
    cmd = ["uvicorn", "run:app"]
    
    if reload:
        cmd.append("--reload")
        
    cmd.extend(["--port", str(port)])
    
    print(f"Starting server on port {port}")
    try:
        # Use os.execvp to replace the current process with uvicorn
        os.execvp(cmd[0], cmd)
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Control the Commercial View FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--kill-existing", action="store_true", help="Kill any existing process using the port")
    
    args = parser.parse_args()
    
    # Check if port is in use
    in_use, pid = check_port_in_use(args.port)
    
    if in_use:
        print(f"Port {args.port} is already in use by process {pid if pid else 'unknown'}")
        
        if args.kill_existing and pid:
            if kill_process(pid):
                # Wait a moment for the port to be released
                import time
                time.sleep(0.5)
            else:
                # Try another port
                args.port += 1
                print(f"Will try port {args.port} instead")
        elif not args.kill_existing:
            # Increment the port if not killing existing process
            args.port += 1
            print(f"Will try port {args.port} instead")
    
    # Start the server
    start_server(port=args.port, reload=not args.no_reload)

if __name__ == "__main__":
    main()
