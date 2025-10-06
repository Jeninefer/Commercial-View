"""
Build script for Commercial-View project
Handles compilation, packaging, and distribution
"""

import os
import subprocess
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

class ProjectBuilder:
    """Build manager for Commercial-View project"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / "dist"
        self.build_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def run_command(self, command, cwd=None):
        """Run command and return success status"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=cwd or self.project_root
            )
            print(f"✅ {command}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ {command}: {e.stderr}")
            return False, e.stderr
    
    def clean_build(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning build artifacts...")
        
        # Remove dist directory
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        # Remove zip files
        for zip_file in self.project_root.glob("*.zip"):
            zip_file.unlink()
        
        print("✅ Build artifacts cleaned")
    
    def compile_typescript(self):
        """Compile TypeScript files"""
        print("🔧 Compiling TypeScript...")
        
        # Check if TypeScript files exist
        ts_dir = self.project_root / "src" / "typescript"
        if not ts_dir.exists():
            print("ℹ️  No TypeScript files found, skipping compilation")
            return True
        
        success, output = self.run_command("npx tsc")
        return success
    
    def install_dependencies(self):
        """Install all project dependencies"""
        print("📦 Installing dependencies...")
        
        # Install root dependencies
        success, _ = self.run_command("npm install")
        if not success:
            return False
        
        # Install frontend dependencies
        frontend_dir = self.project_root / "frontend" / "dashboard"
        if frontend_dir.exists():
            success, _ = self.run_command("npm install", cwd=frontend_dir)
            if not success:
                return False
        
        return True
    
    def build_frontend(self):
        """Build React frontend"""
        print("⚛️  Building React frontend...")
        
        frontend_dir = self.project_root / "frontend" / "dashboard"
        if not frontend_dir.exists():
            print("ℹ️  No frontend directory found, skipping")
            return True
        
        success, _ = self.run_command("npm run build", cwd=frontend_dir)
        return success
    
    def package_project(self):
        """Package the entire project"""
        print("📦 Packaging project...")
        
        # Create dist directory
        self.dist_dir.mkdir(exist_ok=True)
        
        # Package backend
        backend_files = [
            "src/", "scripts/", "*.py", "requirements.txt", 
            "README.md", "setup_guide.ipynb"
        ]
        
        backend_zip = f"commercial-view-backend-{self.build_timestamp}.zip"
        zip_command = f"zip -r {backend_zip} {' '.join(backend_files)} -x '*.pyc' '__pycache__/*' '.venv/*'"
        self.run_command(zip_command)
        
        # Package frontend if exists
        frontend_build = self.project_root / "frontend" / "dashboard" / "build"
        if frontend_build.exists():
            frontend_zip = f"commercial-view-frontend-{self.build_timestamp}.zip"
            self.run_command(f"zip -r {frontend_zip} frontend/dashboard/build/")
        
        # Move zip files to dist
        for zip_file in self.project_root.glob("*.zip"):
            shutil.move(str(zip_file), self.dist_dir / zip_file.name)
        
        print(f"✅ Project packaged in dist/ directory")
        return True
    
    def setup_mcp_servers(self):
        """Setup MCP (Model Context Protocol) servers configuration"""
        print("🔗 Setting up MCP servers configuration...")
        
        # Create MCP configuration
        mcp_config = {
            "mcpServers": {
                "figma": {
                    "command": "npx",
                    "args": ["@figma/mcp-server-figma"],
                    "env": {
                        "FIGMA_PERSONAL_ACCESS_TOKEN": "${FIGMA_PERSONAL_ACCESS_TOKEN}"
                    }
                },
                "commercial-view-api": {
                    "command": "python",
                    "args": ["-m", "commercial_view.mcp_server"],
                    "env": {
                        "API_BASE_URL": "http://localhost:8000",
                        "API_TOKEN": "${COMMERCIAL_VIEW_API_TOKEN}"
                    }
                },
                "github": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
                    }
                }
            }
        }
        
        # Write MCP configuration
        mcp_config_path = self.project_root / "mcp-config.json"
        with open(mcp_config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print("✅ MCP configuration created at mcp-config.json")
        
        # Create environment template
        env_template = """
# MCP Server Configuration
FIGMA_PERSONAL_ACCESS_TOKEN=your_figma_token_here
COMMERCIAL_VIEW_API_TOKEN=your_api_token_here
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here

# Figma MCP Server URLs
FIGMA_MCP_SERVER_URL=npx @figma/mcp-server-figma
FIGMA_API_BASE_URL=https://api.figma.com/v1

# Commercial View API
COMMERCIAL_VIEW_MCP_URL=http://localhost:8000/mcp
COMMERCIAL_VIEW_API_URL=http://localhost:8000
"""
        
        env_file = self.project_root / ".env.mcp"
        with open(env_file, 'w') as f:
            f.write(env_template.strip())
        
        print("✅ MCP environment template created at .env.mcp")
        
        return True
    
    def create_mcp_server_script(self):
        """Create MCP server integration script"""
        print("🖥️  Creating MCP server integration...")
        
        mcp_server_content = '''#!/usr/bin/env python3
"""
MCP Server integration for Commercial-View
Provides Model Context Protocol server functionality
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

class CommercialViewMCPServer:
    """MCP Server for Commercial-View integration"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load MCP configuration"""
        config_path = Path("mcp-config.json")
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}
    
    def get_figma_server_info(self) -> Dict[str, str]:
        """Get Figma MCP server information"""
        return {
            "server_url": "npx @figma/mcp-server-figma",
            "api_base": "https://api.figma.com/v1",
            "documentation": "https://github.com/figma/mcp-server-figma",
            "setup_command": "npm install @figma/mcp-server-figma",
            "usage": "Configure FIGMA_PERSONAL_ACCESS_TOKEN in environment"
        }
    
    def start_figma_server(self):
        """Start Figma MCP server"""
        import subprocess
        
        print("🎨 Starting Figma MCP Server...")
        print("📝 Server URL: npx @figma/mcp-server-figma")
        print("🔗 API Base: https://api.figma.com/v1")
        
        try:
            # Check if Figma MCP server is installed
            result = subprocess.run(
                ["npm", "list", "@figma/mcp-server-figma"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("📦 Installing Figma MCP server...")
                subprocess.run(["npm", "install", "@figma/mcp-server-figma"], check=True)
            
            print("✅ Figma MCP server ready")
            print("💡 Use: npx @figma/mcp-server-figma")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error setting up Figma MCP server: {e}")
    
    def print_mcp_urls(self):
        """Print all MCP server URLs"""
        print("🌐 MCP Server URLs:")
        print("=" * 40)
        
        servers = {
            "Figma MCP Server": {
                "command": "npx @figma/mcp-server-figma",
                "url": "https://github.com/figma/mcp-server-figma",
                "install": "npm install @figma/mcp-server-figma"
            },
            "Commercial-View API": {
                "command": "python run.py",
                "url": "http://localhost:8000",
                "mcp_endpoint": "http://localhost:8000/mcp"
            },
            "GitHub MCP Server": {
                "command": "npx @modelcontextprotocol/server-github",
                "url": "https://github.com/modelcontextprotocol/servers",
                "install": "npm install @modelcontextprotocol/server-github"
            }
        }
        
        for name, info in servers.items():
            print(f"\\n📍 {name}:")
            for key, value in info.items():
                print(f"   {key}: {value}")

def main():
    """Main MCP server function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        server = CommercialViewMCPServer()
        
        if command == "figma":
            server.start_figma_server()
        elif command == "urls":
            server.print_mcp_urls()
        elif command == "info":
            info = server.get_figma_server_info()
            print("🎨 Figma MCP Server Information:")
            for key, value in info.items():
                print(f"   {key}: {value}")
        else:
            print("Available commands: figma, urls, info")
    else:
        server = CommercialViewMCPServer()
        server.print_mcp_urls()

if __name__ == "__main__":
    main()
'''
        
        mcp_script_path = self.project_root / "scripts" / "mcp_server.py"
        with open(mcp_script_path, 'w') as f:
            f.write(mcp_server_content)
        
        # Make executable
        os.chmod(mcp_script_path, 0o755)
        
        print("✅ MCP server script created at scripts/mcp_server.py")
        return True

def main():
    """Main build function"""
    print("🚀 Commercial-View Build Process")
    print("=" * 40)
    
    builder = ProjectBuilder()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "clean":
            builder.clean_build()
            return
        elif command == "install":
            builder.install_dependencies()
            return
        elif command == "compile":
            builder.compile_typescript()
            return
        elif command == "frontend":
            builder.build_frontend()
            return
        elif command == "package":
            builder.package_project()
            return
        elif command == "mcp":
            builder.setup_mcp_servers()
            builder.create_mcp_server_script()
            return
    
    # Full build process
    steps = [
        ("Clean", builder.clean_build),
        ("Install Dependencies", builder.install_dependencies),
        ("Compile TypeScript", builder.compile_typescript),
        ("Build Frontend", builder.build_frontend),
        ("Setup MCP Servers", builder.setup_mcp_servers),
        ("Create MCP Integration", builder.create_mcp_server_script),
        ("Package Project", builder.package_project)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Build failed at step: {step_name}")
            sys.exit(1)
    
    print(f"\n🎉 Build completed successfully!")
    print(f"📁 Build artifacts available in: {builder.dist_dir}")

if __name__ == "__main__":
    main()

{
  "name": "commercial-view",
  "version": "1.0.0",
  "description": "Enterprise-grade portfolio analytics for Abaco Capital",
  "main": "dist/index.js",
  "scripts": {
    "install": "npm install && cd frontend/dashboard && npm install",
    "compile": "tsc",
    "watch": "tsc --watch",
    "package": "npm run compile && npm run package:backend && npm run package:frontend",
    "package:backend": "zip -r commercial-view-backend.zip src/ scripts/ *.py requirements.txt README.md -x '*.pyc' '__pycache__/*'",
    "package:frontend": "cd frontend/dashboard && npm run build && cd ../.. && zip -r commercial-view-frontend.zip frontend/dashboard/build/",
    "start": "python run.py",
    "dev": "python server_control.py --reload",
    "test": "python -m pytest -q",
    "lint": "python -m black src/ scripts/ tests/",
    "type-check": "python -m mypy src/",
    "sync": "python scripts/sync_github.py",
    "upload": "python scripts/upload_to_drive.py",
    "build": "npm run compile && npm run package",
    "clean": "rm -rf dist/ node_modules/ frontend/dashboard/node_modules/ *.zip",
    "setup": "python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "python": ">=3.11.0"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/Jeninefer/Commercial-View.git"
  },
  "keywords": [
    "portfolio",
    "analytics",
    "fastapi",
    "react",
    "finance"
  ],
  "author": "Abaco Capital",
  "license": "PROPRIETARY"
}

{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src/typescript",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "removeComments": false,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "moduleResolution": "node",
    "allowSyntheticDefaultImports": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": [
    "src/typescript/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.test.ts",
    "**/*.spec.ts"
  ]
}
