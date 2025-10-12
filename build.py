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
        self.build_timestamp = datetime.now().isoformat()
        self.version = self._get_version()
        
    def _get_version(self) -> str:
        """Get project version from VERSION file or package.json"""
        version_file = self.project_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        
        # Fallback to package.json if exists
        package_json = self.project_root / "frontend" / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                return data.get("version", "1.0.0")
            except Exception as e:
                pass
        
        return "1.0.0"
    
    def clean_build(self) -> bool:
        """Clean previous build artifacts"""
        print("🧹 Cleaning build artifacts...")
        
        # Remove dist directory
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        # Remove Python cache
        for cache_dir in self.project_root.rglob("__pycache__"):
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir)
        
        # Remove pytest cache
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            shutil.rmtree(pytest_cache)
        
        # Remove frontend build artifacts
        frontend_build = self.project_root / "frontend" / "build"
        if frontend_build.exists():
            shutil.rmtree(frontend_build)
        
        frontend_dist = self.project_root / "frontend" / "dist"
        if frontend_dist.exists():
            shutil.rmtree(frontend_dist)
        
        node_modules = self.project_root / "frontend" / "node_modules"
        if node_modules.exists():
            print("   Removing node_modules...")
            shutil.rmtree(node_modules)
        
        print("✅ Build artifacts cleaned")
        return True
    
    def validate_environment(self) -> bool:
        """Validate build environment"""
        print("🔍 Validating build environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check virtual environment
        if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
            print("⚠️  Virtual environment not detected")
        else:
            print("✅ Virtual environment active")
        
        # Check Node.js for frontend
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js {result.stdout.strip()}")
            else:
                print("⚠️  Node.js not available (frontend builds will be skipped)")
        except FileNotFoundError:
            print("⚠️  Node.js not found (frontend builds will be skipped)")
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python and Node.js dependencies"""
        print("📦 Installing dependencies...")
        
        # Install Python dependencies
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=self.project_root)
            print("✅ Python dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
        
        # Install Node.js dependencies if frontend exists
        frontend_dir = self.project_root / "frontend"
        if frontend_dir.exists() and (frontend_dir / "package.json").exists():
            try:
                subprocess.run([
                    "npm", "install"
                ], check=True, cwd=frontend_dir)
                print("✅ Node.js dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Node.js dependencies: {e}")
                return False
        
        return True
    
    def run_tests(self) -> bool:
        """Run comprehensive test suite"""
        print("🧪 Running test suite...")
        
        # Run Python tests
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
            ], cwd=self.project_root)
            
            if result.returncode != 0:
                print("❌ Python tests failed")
                return False
            print("✅ Python tests passed")
        except FileNotFoundError:
            print("⚠️  pytest not found, skipping Python tests")
        
        # Run frontend tests if available
        frontend_dir = self.project_root / "frontend"
        if frontend_dir.exists() and (frontend_dir / "package.json").exists():
            try:
                result = subprocess.run([
                    "npm", "test", "--", "--watchAll=false", "--coverage"
                ], cwd=frontend_dir)
                
                if result.returncode != 0:
                    print("❌ Frontend tests failed")
                    return False
                print("✅ Frontend tests passed")
            except FileNotFoundError:
                print("⚠️  npm not found, skipping frontend tests")
        
        return True
    
    def lint_code(self) -> bool:
        """Run code linting and formatting checks"""
        print("🎨 Running code quality checks...")
        
        # Python linting
        try:
            # Black formatting check
            result = subprocess.run([
                sys.executable, "-m", "black", "--check", "--dif", "src/", "tests/", "scripts/"
            ], cwd=self.project_root)
            
            if result.returncode != 0:
                print("❌ Python code formatting issues found")
                return False
            print("✅ Python code formatting check passed")
            
            # MyPy type checking
            subprocess.run([
                sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports"
            ], cwd=self.project_root, check=True)
            print("✅ Python type checking passed")
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️  Python linting tools not available: {e}")
        
        # Frontend linting
        frontend_dir = self.project_root / "frontend"
        if frontend_dir.exists():
            try:
                result = subprocess.run([
                    "npm", "run", "lint"
                ], cwd=frontend_dir)
                
                if result.returncode != 0:
                    print("❌ Frontend linting issues found")
                    return False
                print("✅ Frontend linting passed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Frontend linting not available")
        
        return True
    
    def build_backend(self) -> bool:
        """Build Python backend components"""
        print("🐍 Building Python backend...")
        
        # Create dist directory structure
        backend_dist = self.dist_dir / "backend"
        backend_dist.mkdir(parents=True, exist_ok=True)
        
        # Copy source code
        src_dist = backend_dist / "src"
        if (self.project_root / "src").exists():
            shutil.copytree(self.project_root / "src", src_dist)
        
        # Copy configuration files
        config_files = ["requirements.txt", "run.py", "server_control.py"]
        for config_file in config_files:
            src_file = self.project_root / config_file
            if src_file.exists():
                shutil.copy2(src_file, backend_dist)
        
        # Copy configs directory
        configs_dir = self.project_root / "configs"
        if configs_dir.exists():
            shutil.copytree(configs_dir, backend_dist / "configs")
        
        # Copy scripts
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            shutil.copytree(scripts_dir, backend_dist / "scripts")
        
        print("✅ Backend build completed")
        return True
    
    def build_frontend(self) -> bool:
        """Build frontend components"""
        print("🎨 Building frontend...")
        
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            print("⚠️  Frontend directory not found, skipping")
            return True
        
        # Build frontend
        try:
            subprocess.run([
                "npm", "run", "build"
            ], check=True, cwd=frontend_dir)
            
            # Copy build artifacts to dist
            frontend_build = frontend_dir / "build"
            if frontend_build.exists():
                frontend_dist = self.dist_dir / "frontend"
                shutil.copytree(frontend_build, frontend_dist)
            
            print("✅ Frontend build completed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend build failed: {e}")
            return False
    
    def build_documentation(self) -> bool:
        """Build documentation"""
        print("📚 Building documentation...")
        
        docs_dist = self.dist_dir / "docs"
        docs_dist.mkdir(parents=True, exist_ok=True)
        
        # Copy documentation
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                rel_path = doc_file.relative_to(docs_dir)
                dest_path = docs_dist / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(doc_file, dest_path)
        
        # Copy README
        readme = self.project_root / "README.md"
        if readme.exists():
            shutil.copy2(readme, docs_dist)
        
        print("✅ Documentation build completed")
        return True
    
    def create_build_manifest(self) -> bool:
        """Create build manifest file"""
        print("📋 Creating build manifest...")
        
        manifest = {
            "build_info": {
                "version": self.version,
                "timestamp": self.build_timestamp,
                "builder": "Commercial-View Build System v1.0.0",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            },
            "components": {
                "backend": (self.dist_dir / "backend").exists(),
                "frontend": (self.dist_dir / "frontend").exists(), 
                "documentation": (self.dist_dir / "docs").exists()
            },
            "files": []
        }
        
        # List all files in distribution
        for file_path in self.dist_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.dist_dir)
                manifest["files"].append({
                    "path": str(rel_path),
                    "size": file_path.stat().st_size
                })
        
        # Write manifest
        manifest_file = self.dist_dir / "build_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Build manifest created: {len(manifest['files'])} files")
        return True
    
    def create_deployment_package(self) -> Optional[Path]:
        """Create deployment package"""
        print("📦 Creating deployment package...")
        
        package_name = f"commercial-view-{self.version}-{datetime.now().strftime('%Y%m%d')}"
        package_path = self.project_root / f"{package_name}.zip"
        
        try:
            # Create zip archive
            shutil.make_archive(
                str(self.project_root / package_name),
                'zip',
                self.dist_dir
            )
            
            print(f"✅ Deployment package created: {package_path}")
            return package_path
            
        except Exception as e:
            print(f"❌ Failed to create deployment package: {e}")
            return None
    
    def build_all(self, skip_tests: bool = False, skip_lint: bool = False) -> bool:
        """Run complete build process"""
        print(f"🚀 Starting Commercial-View build v{self.version}")
        print("=" * 60)
        
        build_steps = [
            ("Validate Environment", self.validate_environment),
            ("Clean Build", self.clean_build),
            ("Install Dependencies", self.install_dependencies),
        ]
        
        if not skip_lint:
            build_steps.append(("Lint Code", self.lint_code))
        
        if not skip_tests:
            build_steps.append(("Run Tests", self.run_tests))
        
        build_steps.extend([
            ("Build Backend", self.build_backend),
            ("Build Frontend", self.build_frontend),
            ("Build Documentation", self.build_documentation),
            ("Create Manifest", self.create_build_manifest),
        ])
        
        # Execute build steps
        for step_name, step_func in build_steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"❌ Build failed at step: {step_name}")
                return False
        
        # Create deployment package
        package_path = self.create_deployment_package()
        
        print("\n🎉 Build completed successfully!")
        print(f"Version: {self.version}")
        print(f"Build time: {self.build_timestamp}")
        print(f"Distribution: {self.dist_dir}")
        if package_path:
            print(f"Package: {package_path}")
        
        return True

def main():
    """Main build script entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Commercial-View Build System")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    parser.add_argument("--skip-lint", action="store_true", help="Skip code linting")
    parser.add_argument("--clean-only", action="store_true", help="Only clean build artifacts")
    parser.add_argument("--version", action="version", version="Commercial-View Build System v1.0.0")
    
    args = parser.parse_args()
    
    builder = ProjectBuilder()
    
    if args.clean_only:
        success = builder.clean_build()
    else:
        success = builder.build_all(
            skip_tests=args.skip_tests,
            skip_lint=args.skip_lint
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
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
            f.write("Commercial-View Build Report\n")
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
