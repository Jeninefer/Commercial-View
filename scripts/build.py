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
from typing import Tuple, Optional, List

class ProjectBuilder:
    """Build manager for Commercial-View project"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / "dist"
        self.build_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.build_log: List[str] = []
    
    def log(self, message: str) -> None:
        """Log a build message"""
        self.build_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        print(message)
    
    def run_command(self, command: str, cwd: Optional[Path] = None) -> Tuple[bool, str]:
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
            self.log(f"✅ {command}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"❌ {command}: {e.stderr}")
            return False, e.stderr
    
    def validate_environment(self) -> bool:
        """Validate build environment requirements"""
        self.log("🔍 Validating build environment...")
        
        # Check if we're in the correct directory
        if not (self.project_root / "package.json").exists():
            self.log("❌ package.json not found - not in project root?")
            return False
        
        # Check for Python
        success, version = self.run_command("python --version")
        if not success:
            self.log("❌ Python not found")
            return False
        else:
            self.log(f"✅ Python found: {version.strip()}")
        
        # Check for Node.js
        success, version = self.run_command("node --version")
        if not success:
            self.log("❌ Node.js not found")
            return False
        else:
            self.log(f"✅ Node.js found: {version.strip()}")
        
        # Check for npm
        success, version = self.run_command("npm --version")
        if success:
            self.log(f"✅ npm found: {version.strip()}")
        
        self.log("✅ Environment validation passed")
        return True

    def clean_build(self) -> bool:
        """Clean previous build artifacts"""
        self.log("🧹 Cleaning build artifacts...")
        
        try:
            # Remove dist directory
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
                self.log("✅ Removed dist/ directory")
            
            # Remove zip files
            zip_count = 0
            for zip_file in self.project_root.glob("*.zip"):
                zip_file.unlink()
                zip_count += 1
            
            if zip_count > 0:
                self.log(f"✅ Removed {zip_count} zip files")
            
            # Remove node_modules for fresh install
            node_modules = self.project_root / "node_modules"
            if node_modules.exists():
                shutil.rmtree(node_modules)
                self.log("✅ Removed node_modules for fresh install")
            
            self.log("✅ Build artifacts cleaned")
            return True
        except Exception as e:
            self.log(f"❌ Error cleaning build artifacts: {e}")
            return False
    
    def compile_typescript(self) -> bool:
        """Compile TypeScript files"""
        self.log("🔧 Compiling TypeScript...")
        
        # Check if TypeScript files exist
        ts_dir = self.project_root / "src" / "typescript"
        if not ts_dir.exists():
            self.log("ℹ️  No TypeScript files found, skipping compilation")
            return True
        
        # Install TypeScript if not available
        success, _ = self.run_command("npx tsc --version")
        if not success:
            self.log("📦 Installing TypeScript...")
            success, _ = self.run_command("npm install -g typescript")
            if not success:
                self.log("❌ Failed to install TypeScript")
                return False
        
        success, _ = self.run_command("npx tsc")
        if success:
            self.log("✅ TypeScript compilation completed")
        return success
    
    def install_dependencies(self) -> bool:
        """Install all project dependencies"""
        self.log("📦 Installing dependencies...")
        
        # Install root dependencies
        success, _ = self.run_command("npm install")
        if not success:
            self.log("❌ Failed to install root dependencies")
            return False
        
        self.log("✅ Root dependencies installed")
        
        # Install frontend dependencies
        frontend_dir = self.project_root / "frontend" / "dashboard"
        if frontend_dir.exists():
            self.log("📦 Installing frontend dependencies...")
            success, _ = self.run_command("npm install", cwd=frontend_dir)
            if not success:
                self.log("❌ Failed to install frontend dependencies")
                return False
            self.log("✅ Frontend dependencies installed")
        
        # Install Python dependencies if requirements.txt exists
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            self.log("🐍 Installing Python dependencies...")
            success, _ = self.run_command("pip install -r requirements.txt")
            if success:
                self.log("✅ Python dependencies installed")
            else:
                self.log("⚠️  Python dependencies installation failed (continuing anyway)")
        
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
        
        print("✅ Project packaged in dist/ directory")
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
        with open(mcp_config_path, 'w', encoding='utf-8') as f:
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
        with open(env_file, 'w', encoding='utf-8') as f:
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
            with open(config_path, encoding='utf-8') as f:
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
                text=True,
                check=False
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
        with open(mcp_script_path, 'w', encoding='utf-8') as f:
            f.write(mcp_server_content)
        
        # Make executable
        os.chmod(mcp_script_path, 0o755)
        
        print("✅ MCP server script created at scripts/mcp_server.py")
        return True

    def create_package_json_if_missing(self) -> None:
        """Create package.json if it doesn't exist"""
        package_json_path = self.project_root / "package.json"
        if not package_json_path.exists():
            print("📦 Creating package.json...")
            
            package_config = {
                "name": "commercial-view",
                "version": "1.0.0",
                "description": "Enterprise-grade portfolio analytics for Abaco Capital",
                "main": "dist/index.js",
                "scripts": {
                    "compile": "tsc",
                    "watch": "tsc --watch",
                    "build": "python scripts/build.py",
                    "start": "python run.py",
                    "test": "python -m pytest -q",
                    "lint": "python -m black src/ scripts/",
                    "sync": "python scripts/sync_github.py"
                },
                "devDependencies": {
                    "@types/node": "^20.0.0",
                    "typescript": "^5.0.0"
                },
                "engines": {
                    "node": ">=18.0.0",
                    "python": ">=3.11.0"
                }
            }
            
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_config, f, indent=2)
            
            print("✅ package.json created")

    def create_tsconfig_if_missing(self) -> None:
        """Create tsconfig.json if it doesn't exist"""
        tsconfig_path = self.project_root / "tsconfig.json"
        if not tsconfig_path.exists():
            print("📝 Creating tsconfig.json...")
            
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "lib": ["ES2020"],
                    "outDir": "./dist",
                    "rootDir": "./src/typescript",
                    "strict": True,
                    "esModuleInterop": True,
                    "skipLibCheck": True,
                    "forceConsistentCasingInFileNames": True,
                    "declaration": True,
                    "sourceMap": True
                },
                "include": ["src/typescript/**/*"],
                "exclude": ["node_modules", "dist", "**/*.test.ts"]
            }
            
            with open(tsconfig_path, 'w', encoding='utf-8') as f:
                json.dump(tsconfig, f, indent=2)
            
            print("✅ tsconfig.json created")

    def generate_build_report(self) -> None:
        """Generate a build report"""
        report_path = self.dist_dir / f"build-report-{self.build_timestamp}.txt"
        self.dist_dir.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Commercial-View Build Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Build ID: {self.build_timestamp}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Build Log:\n")
            f.write("-" * 20 + "\n")
            for log_entry in self.build_log:
                f.write(f"{log_entry}\n")
            
            f.write(f"\nBuild completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.log(f"📄 Build report saved to: {report_path}")
    
    def create_deployment_config(self) -> bool:
        """Create deployment configuration files"""
        self.log("🚀 Creating deployment configuration...")
        
        # Create Docker configuration
        dockerfile_content = '''# Commercial-View Dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/dashboard/package*.json ./
RUN npm install
COPY frontend/dashboard/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY run.py .
COPY --from=frontend-builder /app/frontend/build ./static/
EXPOSE 8000
CMD ["python", "run.py"]
'''
        
        dockerfile_path = self.project_root / "Dockerfile"
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        # Create docker-compose configuration
        compose_content = '''version: '3.8'
services:
  commercial-view:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - API_BASE_URL=http://localhost:8000
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: commercial_view
      POSTGRES_USER: commercial_view
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
'''
        
        compose_path = self.project_root / "docker-compose.yml"
        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        
        self.log("✅ Deployment configuration created")
        return True

def main():
    """Main build function"""
    print("🚀 Commercial-View Build Process")
    print("=" * 40)
    
    builder = ProjectBuilder()
    
    # Validate environment first
    if not builder.validate_environment():
        builder.log("❌ Environment validation failed")
        sys.exit(1)
    
    # Create config files if missing
    builder.create_package_json_if_missing()
    builder.create_tsconfig_if_missing()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        command_map = {
            "clean": builder.clean_build,
            "install": builder.install_dependencies,
            "compile": builder.compile_typescript,
            "frontend": builder.build_frontend,
            "package": builder.package_project,
            "mcp": lambda: (builder.setup_mcp_servers() and builder.create_mcp_server_script()),
            "deploy": builder.create_deployment_config,
            "report": builder.generate_build_report,
        }
        
        if command in command_map:
            result = command_map[command]()
            if not result:
                builder.log(f"❌ Command '{command}' failed")
                builder.generate_build_report()
                sys.exit(1)
            builder.generate_build_report()
            return
        else:
            builder.log(f"❌ Unknown command: {command}")
            print("Available commands: clean, install, compile, frontend, package, mcp, deploy, report")
            sys.exit(1)
    
    # Full build process
    steps = [
        ("Clean", builder.clean_build),
        ("Install Dependencies", builder.install_dependencies),
        ("Compile TypeScript", builder.compile_typescript),
        ("Build Frontend", builder.build_frontend),
        ("Setup MCP Servers", builder.setup_mcp_servers),
        ("Create MCP Integration", builder.create_mcp_server_script),
        ("Create Deployment Config", builder.create_deployment_config),
        ("Package Project", builder.package_project)
    ]
    
    for step_name, step_func in steps:
        builder.log(f"\n🔄 {step_name}...")
        if not step_func():
            builder.log(f"❌ Build failed at step: {step_name}")
            builder.generate_build_report()
            sys.exit(1)
    
    # Generate final build report
    builder.generate_build_report()
    
    builder.log("\n🎉 Build completed successfully!")
    builder.log(f"📁 Build artifacts available in: {builder.dist_dir}")

if __name__ == "__main__":
    main()
