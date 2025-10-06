#!/usr/bin/env python3
"""
Debug server script for Commercial-View with remote debugging support
"""

import debugpy
import sys
import os
from pathlib import Path

def start_debug_server(port=5678, wait_for_client=True):
    """Start the API server with debugpy remote debugging enabled"""
    print(f"🐛 Starting Commercial-View with remote debugging on port {port}")
    
    # Configure debugpy
    debugpy.configure(python=sys.executable)
    debugpy.listen(port)
    
    if wait_for_client:
        print(f"⏳ Waiting for debugger to attach on port {port}...")
        debugpy.wait_for_client()
        print("🔗 Debugger attached!")
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))
    
    # Set debug environment
    os.environ["DEBUG"] = "true"
    os.environ["ENVIRONMENT"] = "development"
    
    # Import and run the application
    try:
        from run import app
        import uvicorn
        
        print("🚀 Starting Commercial-View API server in debug mode...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload in debug mode
            log_level="debug"
        )
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Commercial-View with debugging")
    parser.add_argument("--port", type=int, default=5678, help="Debug port (default: 5678)")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for debugger to attach")
    
    args = parser.parse_args()
    
    start_debug_server(port=args.port, wait_for_client=not args.no_wait)
