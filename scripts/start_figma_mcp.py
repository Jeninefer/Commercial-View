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
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing Figma token: {e}")
        return False

def check_figma_mcp_package():
    """Check if Figma MCP package exists and find correct name"""
    print("🔍 Checking available Figma MCP packages...")
    
    # Try different possible package names
    possible_packages = [
        "@figma/mcp-server-figma",
        "@modelcontextprotocol/server-figma", 
        "figma-mcp-server",
        "mcp-server-figma"
    ]
    
    for package in possible_packages:
        try:
            result = subprocess.run(
                ["npm", "view", package, "name"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ Found package: {package}")
                return package
            else:
                print(f"❌ Package not found: {package}")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            print(f"❌ Error checking package: {package}")
    
    print("⚠️  No Figma MCP package found in npm registry")
    return None

def create_custom_figma_server():
    """Create a simple custom Figma MCP server"""
    print("🔨 Creating custom Figma MCP integration...")
    
    server_script = """
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const FIGMA_TOKEN = process.env.FIGMA_PERSONAL_ACCESS_TOKEN;

// Basic Figma API proxy endpoints
app.get('/figma/me', async (req, res) => {
    try {
        const fetch = await import('node-fetch');
        const response = await fetch.default('https://api.figma.com/v1/me', {
            headers: {
                'X-Figma-Token': FIGMA_TOKEN
            }
        });
        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/figma/files/:key', async (req, res) => {
    try {
        const fetch = await import('node-fetch');
        const response = await fetch.default(`https://api.figma.com/v1/files/${req.params.key}`, {
            headers: {
                'X-Figma-Token': FIGMA_TOKEN
            }
        });
        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const port = process.env.PORT || 3001;
app.listen(port, () => {
    console.log(`🎨 Custom Figma MCP server running on port ${port}`);
    console.log(`Token: ${FIGMA_TOKEN ? FIGMA_TOKEN.substring(0, 10) + '...' : 'Not set'}`);
});
"""
    
    # Write the custom server
    with open("figma-mcp-server.js", "w") as f:
        f.write(server_script)
    
    print("✅ Created custom Figma MCP server: figma-mcp-server.js")
    return "figma-mcp-server.js"

def start_figma_mcp_server():
    """Start Figma MCP server with token"""
    print("🎨 Starting Figma MCP Server...")
    
    # Set environment variable
    os.environ["FIGMA_PERSONAL_ACCESS_TOKEN"] = "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
    
    # Test token first
    if not test_figma_token():
        print("❌ Token validation failed")
        return False
    
    # Check if official package exists
    package_name = check_figma_mcp_package()
    
    if package_name:
        try:
            print(f"🚀 Starting {package_name}...")
            subprocess.run(["npx", package_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start {package_name}: {e}")
            print("🔄 Falling back to custom server...")
            return start_custom_server()
    else:
        print("📦 Official Figma MCP package not available")
        print("🔄 Using custom Figma MCP integration...")
        return start_custom_server()
    
    return True

def start_custom_server():
    """Start custom Figma MCP server"""
    try:
        # Install required dependencies
        print("📦 Installing dependencies...")
        subprocess.run(["npm", "install", "express", "cors", "node-fetch"], check=True)
        
        # Create custom server
        server_file = create_custom_figma_server()
        
        # Start custom server
        print("🚀 Starting custom Figma MCP server...")
        subprocess.run(["node", server_file], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start custom server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Figma MCP server stopped by user")
        return True
    
    return True

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "test":
            test_figma_token()
        elif command == "check":
            check_figma_mcp_package()
        elif command == "custom":
            start_custom_server()
        else:
            print("Available commands: test, check, custom")
    else:
        start_figma_mcp_server()

if __name__ == "__main__":
    main()
