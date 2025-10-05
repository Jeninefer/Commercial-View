"""
Script to check Git synchronization status and identify missing files
"""

import os
import subprocess
import glob
from pathlib import Path

def run_git_command(command):
    """Run git command and return output"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

def check_project_files():
    """Check all important project files"""
    important_files = [
        "README.md",
        "setup_guide.ipynb", 
        "requirements.txt",
        "server_control.py",
        "run.py",
        "src/data_loader.py",
        "src/api.py",
        "src/utils/schema_converter.py",
        "scripts/upload_to_drive.py",
        "scripts/sync_github.py",
        "frontend/dashboard/README.md",
        "frontend/dashboard/package.json",
        ".gitignore"
    ]
    
    print("📁 Checking important project files:")
    missing_files = []
    
    for file_path in important_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return missing_files

def main():
    print("🔍 Commercial-View Sync Status Check")
    print("=" * 50)
    
    # Check git status
    print("\n📊 Git Status:")
    status = run_git_command(["git", "status", "--porcelain"])
    if status:
        print("Modified/Untracked files:")
        for line in status.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("  No changes detected")
    
    # Check branch
    branch = run_git_command(["git", "branch", "--show-current"])
    print(f"\n📍 Current branch: {branch}")
    
    # Check remote URL
    remote = run_git_command(["git", "remote", "-v"])
    print(f"\n🔗 Remote repositories:")
    for line in remote.split('\n'):
        if line.strip():
            print(f"  {line}")
    
    # Check important files
    print(f"\n📋 Project Files Status:")
    missing_files = check_project_files()
    
    if missing_files:
        print(f"\n⚠️  Missing files detected: {len(missing_files)}")
        print("Run the following commands to check:")
        print("  ls -la")
        print("  find . -name '*.py' | head -10")
        print("  find . -name '*.md' | head -10")
    else:
        print(f"\n✅ All important files are present")
    
    # Suggest actions
    print(f"\n🔧 Suggested Actions:")
    print("1. Add all files: git add .")
    print("2. Check what will be committed: git status")
    print("3. Commit changes: git commit -m 'Complete project sync'")  
    print("4. Push to GitHub: git push origin main")
    print("5. Verify on GitHub web interface")

if __name__ == "__main__":
    main()
