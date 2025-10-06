#!/usr/bin/env python3
"""
Enhanced Uvicorn server management for Commercial-View
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import Optional, Dict, Any

class UvicornManager:
    """Manage Uvicorn server for Commercial-View"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.app_module = "run:app"
        self.default_host = "0.0.0.0"
        self.default_port = 8000
        
    def load_environment(self) -> None:
        """Load Commercial-View environment variables"""
        # Set project paths
        os.environ["COMMERCIAL_VIEW_ROOT"] = str(self.project_root)
        os.environ["PYTHONPATH"] = f"{self.project_root}/src:{os.environ.get('PYTHONPATH', '')}"
        
        # Load .env file if it exists
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file, encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    def start_server(
        self, 
        host: str = None,
        port: int = None,
        reload: bool = True,
        workers: int = 1,
        log_level: str = "info",
        access_log: bool = True
    ) -> None:
        """Start Uvicorn server with Commercial-View configuration"""
        
        self.load_environment()
        
        host = host or self.default_host
        port = port or self.default_port
        
        cmd = [
            sys.executable, "-m", "uvicorn", self.app_module,
            "--host", host,
            "--port", str(port),
            "--log-level", log_level
        ]
        
        if reload:
            cmd.extend(["--reload", "--reload-dir", "src", "--reload-dir", "scripts"])
        
        if workers > 1 and not reload:
            cmd.extend(["--workers", str(workers)])
        
        if access_log:
            cmd.append("--access-log")
        
        print(f"🚀 Starting Commercial-View server on {host}:{port}")
        print(f"📁 Project root: {self.project_root}")
        print(f"🔧 Command: {' '.join(cmd)}")
        
        try:
            os.chdir(self.project_root)
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    
    def start_development_server(self) -> None:
        """Start server with development settings"""
        self.start_server(
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="debug",
            access_log=True
        )
    
    def start_production_server(self) -> None:
        """Start server with production settings"""
        self.start_server(
            host="0.0.0.0",
            port=8000,
            reload=False,
            workers=4,
            log_level="info",
            access_log=False
        )
    
    def check_server_health(self, host: str = "localhost", port: int = 8000) -> bool:
        """Check if server is running and healthy"""
        try:
            import requests
            response = requests.get(f"http://{host}:{port}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def kill_server_on_port(self, port: int = 8000) -> bool:
        """Kill any server running on the specified port"""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"🔪 Killed process {pid} on port {port}")
                    except ProcessLookupError:
                        pass
                return True
            else:
                print(f"ℹ️ No processes found on port {port}")
                return False
                
        except Exception as e:
            print(f"❌ Error killing processes: {e}")
            return False

def main():
    """Main Uvicorn management function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Commercial-View Uvicorn server")
    parser.add_argument("action", choices=["dev", "prod", "kill", "health"],
                       help="Action to perform")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    manager = UvicornManager()
    
    if args.action == "dev":
        manager.start_development_server()
    elif args.action == "prod":
        manager.start_production_server()
    elif args.action == "kill":
        manager.kill_server_on_port(args.port)
    elif args.action == "health":
        healthy = manager.check_server_health(args.host, args.port)
        print(f"Server health: {'✅ Healthy' if healthy else '❌ Unhealthy'}")
        return 0 if healthy else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
