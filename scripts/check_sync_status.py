"""
Script to check Git synchronization status and identify missing files
"""

import os
import subprocess
from pathlib import Path
from typing import List

def run_git_command(command: List[str]) -> str:
    """Run git command and return output"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

def check_project_files() -> List[str]:
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

def display_git_status() -> None:
    """Display current git status"""
    print("\n📊 Git Status:")
    status = run_git_command(["git", "status", "--porcelain"])
    if status and not status.startswith("Error:"):
        print("Modified/Untracked files:")
        for line in status.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("  No changes detected")

def display_branch_info() -> None:
    """Display current branch information"""
    branch = run_git_command(["git", "branch", "--show-current"])
    print(f"\n📍 Current branch: {branch}")

def display_remote_info() -> None:
    """Display remote repository information"""
    remote = run_git_command(["git", "remote", "-v"])
    print("\n🔗 Remote repositories:")
    if remote and not remote.startswith("Error:"):
        for line in remote.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("  No remote repositories configured")

def display_suggested_actions() -> None:
    """Display suggested actions for sync"""
    print("\n🔧 Suggested Actions:")
    print("1. Add all files: git add .")
    print("2. Check what will be committed: git status")
    print("3. Commit changes: git commit -m 'Complete project sync'")  
    print("4. Push to GitHub: git push origin main")
    print("5. Verify on GitHub web interface")

def main():
    """Main function to check sync status"""
    print("🔍 Commercial-View Sync Status Check")
    print("=" * 50)
    
    # Display git information
    display_git_status()
    display_branch_info()
    display_remote_info()
    
    # Check important files
    print("\n📋 Project Files Status:")
    missing_files = check_project_files()
    
    if missing_files:
        print(f"\n⚠️  Missing files detected: {len(missing_files)}")
        print("Run the following commands to check:")
        print("  ls -la")
        print("  find . -name '*.py' | head -10")
        print("  find . -name '*.md' | head -10")
    else:
        print("\n✅ All important files are present")
    
    # Display suggested actions
    display_suggested_actions()

if __name__ == "__main__":
    main()
