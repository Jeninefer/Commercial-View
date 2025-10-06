"""
Enhanced helper script to install Google Drive API dependencies and Commercial-View platform requirements
"""

import subprocess
import sys
import os
import importlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional


def check_python_version() -> bool:
    """Check if Python version meets requirements"""
    print("🐍 Checking Python version...")

    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        print("💡 Please upgrade Python before installing dependencies")
        return False

    print(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - Compatible"
    )
    return True


def check_virtual_environment() -> bool:
    """Check if running in virtual environment"""
    print("🔍 Checking virtual environment...")

    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        print("💡 Consider creating a virtual environment: python -m venv .venv")
        return False


def install_package(package: str, version: Optional[str] = None) -> Tuple[bool, str]:
    """Install a single package with enhanced error handling"""
    package_spec = f"{package}=={version}" if version else package

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_spec],
            capture_output=True,
            text=True,
            check=True,
        )

        return True, result.stdout

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        return False, error_msg


def test_package_import(package: str, import_name: Optional[str] = None) -> bool:
    """Test if package can be imported successfully"""
    test_name = import_name or package.replace("-", "_")

    try:
        importlib.import_module(test_name)
        return True
    except ImportError:
        return False


def install_google_drive_dependencies() -> bool:
    """Install all required Google Drive API dependencies with enhanced validation"""
    print("🚀 Installing Google Drive API Dependencies for Commercial-View")
    print("=" * 60)

    # Check prerequisites
    if not check_python_version():
        return False

    check_virtual_environment()

    # Core Google Drive packages
    core_packages = [
        ("google-auth", "2.23.4", "google.auth"),
        ("google-auth-oauthlib", "1.1.0", "google_auth_oauthlib"),
        ("google-api-python-client", "2.109.0", "googleapiclient"),
        ("google-auth-httplib2", "0.2.0", "google_auth_httplib2"),
    ]

    # Commercial lending data processing packages
    data_packages = [
        ("pandas", "2.1.3", "pandas"),
        ("numpy", "1.25.2", "numpy"),
        ("openpyxl", "3.1.2", "openpyxl"),
        ("xlsxwriter", "3.1.9", "xlsxwriter"),
    ]

    # Additional utility packages
    utility_packages = [
        ("requests", "2.31.0", "requests"),
        ("tqdm", "4.66.1", "tqdm"),
        ("python-dateutil", "2.8.2", "dateutil"),
    ]

    all_packages = core_packages + data_packages + utility_packages

    print(f"📦 Installing {len(all_packages)} packages...")

    success_count = 0
    failed_packages = []

    for package, version, import_name in all_packages:
        print(f"\n📦 Installing {package}=={version}...")

        # Check if already installed
        if test_package_import(package, import_name):
            print(f"✅ {package} already installed and working")
            success_count += 1
            continue

        # Install package
        success, output = install_package(package, version)

        if success:
            # Verify installation by importing
            if test_package_import(package, import_name):
                print(f"✅ Successfully installed and verified {package}")
                success_count += 1
            else:
                print(f"⚠️  {package} installed but import test failed")
                failed_packages.append(package)
        else:
            print(f"❌ Failed to install {package}")
            print(f"   Error: {output}")
            failed_packages.append(package)

    # Install additional Commercial-View specific packages
    print(f"\n🏦 Installing Commercial-View specific packages...")

    commercial_packages = [
        ("pyyaml", "6.0.1", "yaml"),
        ("pydantic", "2.5.0", "pydantic"),
        ("fastapi", "0.104.1", "fastapi"),
        ("uvicorn", "0.24.0", "uvicorn"),
    ]

    for package, version, import_name in commercial_packages:
        print(f"\n📦 Installing {package}=={version}...")

        if test_package_import(package, import_name):
            print(f"✅ {package} already installed and working")
            success_count += 1
            continue

        success, output = install_package(package, version)

        if success and test_package_import(package, import_name):
            print(f"✅ Successfully installed {package}")
            success_count += 1
        else:
            print(f"❌ Failed to install or verify {package}")
            failed_packages.append(package)

    total_packages = len(all_packages) + len(commercial_packages)

    # Generate installation report
    print(f"\n📊 Installation Summary:")
    print(f"   Successful: {success_count}/{total_packages}")
    print(f"   Failed: {len(failed_packages)}")

    if failed_packages:
        print(f"\n❌ Failed packages: {', '.join(failed_packages)}")

    if success_count == total_packages:
        print("\n🎉 All dependencies installed successfully!")
        print("✅ Commercial-View Google Drive integration is ready")
        print("\n🚀 Available features:")
        print("   - Commercial lending data export to Google Drive")
        print("   - KPI report uploads")
        print("   - Portfolio analysis file sharing")
        print("   - Regulatory report distribution")

        # Create configuration template
        create_drive_config_template()

        return True
    else:
        print("\n⚠️  Some dependencies failed to install")
        print("💡 Troubleshooting steps:")
        print("   1. Ensure you're in a virtual environment")
        print("   2. Update pip: python -m pip install --upgrade pip")
        print("   3. Check internet connection")
        print("   4. Try installing failed packages individually")
        return False


def create_drive_config_template() -> None:
    """Create Google Drive configuration template for Commercial-View"""
    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)

    config_content = """# Google Drive Configuration for Commercial-View
# Copy this to google_drive_config.yml and update with your settings

google_drive:
  # Google Drive API credentials file
  credentials_file: "secrets/google-drive-credentials.json"
  
  # Commercial lending export folders
  folders:
    kpi_reports: "Commercial-View/KPI Reports"
    portfolio_analysis: "Commercial-View/Portfolio Analysis"
    regulatory_reports: "Commercial-View/Regulatory Reports"
    pricing_matrices: "Commercial-View/Pricing Matrices"
    risk_assessments: "Commercial-View/Risk Assessments"
  
  # File naming conventions
  naming:
    timestamp_format: "%Y%m%d_%H%M%S"
    include_branch: true
    include_version: true
  
  # Upload settings
  upload:
    chunk_size: 1048576  # 1MB chunks
    timeout: 300  # 5 minutes
    retry_attempts: 3
    
  # Commercial lending specific settings
  commercial_lending:
    # Supported export formats
    formats: ["csv", "xlsx", "json", "pdf"]
    
    # Data validation before upload
    validate_before_upload: true
    
    # Encryption for sensitive data
    encrypt_sensitive_data: true
"""

    config_file = config_dir / "google_drive_config_template.yml"
    config_file.write_text(config_content)

    print(f"\n📄 Created configuration template: {config_file}")
    print("💡 Copy to google_drive_config.yml and customize for your setup")


def setup_credentials_directory() -> None:
    """Setup directory structure for Google Drive credentials"""
    secrets_dir = Path("secrets")
    secrets_dir.mkdir(exist_ok=True)

    gitignore_file = secrets_dir / ".gitignore"
    gitignore_content = """# Never commit sensitive credentials
*.json
*.key
*.pem
credentials*
service-account*
"""

    gitignore_file.write_text(gitignore_content)

    readme_file = secrets_dir / "README.md"
    readme_content = """# Google Drive Credentials

This directory contains sensitive Google Drive API credentials.

## Setup Instructions

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google Drive API
4. Create credentials (Service Account recommended for server applications)
5. Download credentials JSON file
6. Place credentials file in this directory
7. Update `google_drive_config.yml` with the correct file path

## Security Notes

- Credentials files are automatically ignored by Git
- Never commit credentials to version control
- Use environment variables in production
- Regularly rotate credentials for security
"""

    readme_file.write_text(readme_content)

    print(f"\n🔐 Setup credentials directory: {secrets_dir}")
    print("📖 See secrets/README.md for setup instructions")


def main():
    """Enhanced main function with comprehensive setup"""
    try:
        # Install dependencies
        success = install_google_drive_dependencies()

        if success:
            # Setup additional project structure
            setup_credentials_directory()

            print("\n🎯 Next Steps:")
            print("1. Setup Google Drive API credentials (see secrets/README.md)")
            print(
                "2. Copy configs/google_drive_config_template.yml to google_drive_config.yml"
            )
            print("3. Customize configuration for your Commercial-View setup")
            print("4. Test integration: python scripts/upload_to_drive.py --test")

            return 0
        else:
            print("\n❌ Installation failed")
            print("💡 Please resolve dependency issues before proceeding")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  Installation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
