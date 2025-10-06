#!/usr/bin/env python3
"""
Start Figma MCP server with configured token
"""

import os
import subprocess
import sys
import requests

def test_figma_token():
    """Test if Figma token is working"""
    token = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    
    headers = {
        "X-Figma-Token": token
    }
    
    try:
        response = requests.get("https://api.figma.com/v1/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Figma token valid for user: {user_info.get('email', 'Unknown')}")
            return True
        else:
            print(f"❌ Figma token test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Figma token: {e}")
        return False

def start_figma_mcp_server():
    """Start Figma MCP server with token"""
    print("🎨 Starting Figma MCP Server...")
    
    # Set environment variable
    os.environ["FIGMA_PERSONAL_ACCESS_TOKEN"] = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    
    try:
        # Test token first
        if not test_figma_token():
            print("❌ Token validation failed, but continuing...")
        
        # Start MCP server
        print("🚀 Starting npx @figma/mcp-server-figma...")
        subprocess.run(["npx", "@figma/mcp-server-figma"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Figma MCP server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Figma MCP server stopped by user")
        return True
    
    return True

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_figma_token()
    else:
        start_figma_mcp_server()

if __name__ == "__main__":
    main()
