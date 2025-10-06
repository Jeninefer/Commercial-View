"""
Helper script to install Google Drive API dependencies
"""

import subprocess
import sys

def install_google_drive_dependencies():
    """Install all required Google Drive API dependencies"""
    print("🚀 Installing Google Drive API Dependencies")
    print("=" * 50)
    
    packages = [
        "google-auth-oauthlib",
        "google-api-python-client", 
        "google-auth-httplib2",
        "google-auth"
    ]
    
    success_count = 0
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            
            print(f"✅ Successfully installed {package}")
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            print(f"   Error: {e.stderr}")
    
    print(f"\n📊 Installation Summary:")
    print(f"   Successful: {success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("\n🎉 All dependencies installed successfully!")
        print("✅ You can now run upload_to_drive.py")
        return True
    else:
        print("\n⚠️  Some dependencies failed to install")
        print("💡 Try running with elevated permissions or check your internet connection")
        return False

if __name__ == "__main__":
    success = install_google_drive_dependencies()
    sys.exit(0 if success else 1)
