"""
Complete synchronization script for Commercial-View project
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, check=True):
    """Run command and return result"""
    print(f"🔧 Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr.strip()}")
        return False, e.stderr.strip()

def main():
    """Main sync function"""
    print("🚀 Commercial-View Complete Sync")
    print("=" * 40)
    
    # Step 1: Check current directory
    print(f"\n📍 Current directory: {os.getcwd()}")
    
    # Step 2: Git status
    print("\n1️⃣ Checking Git status...")
    success, _ = run_command(["git", "status", "--short"])
    
    # Step 3: Add all files
    print("\n2️⃣ Adding all files...")
    run_command(["git", "add", "."])
    run_command(["git", "add", "-A"])  # Also add deleted files
    
    # Step 4: Show what's staged
    print("\n3️⃣ Checking staged files...")
    run_command(["git", "status", "--short"])
    
    # Step 5: Commit
    print("\n4️⃣ Creating commit...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Complete sync: Commercial-View project update ({timestamp})"
    success, _ = run_command(["git", "commit", "-m", commit_msg], check=False)
    
    if not success:
        print("ℹ️  No changes to commit or commit failed")
    
    # Step 6: Push to remote  
    print("\n5️⃣ Pushing to GitHub...")
    success, _ = run_command(["git", "push", "origin", "main"], check=False)
    
    if success:
        print("\n🎉 Sync completed successfully!")
    else:
        print("\n⚠️  Push failed - check network connection and credentials")
    
    # Step 7: Show final status
    print("\n6️⃣ Final status:")
    run_command(["git", "status"])
    
    print("\n📝 Next steps:")
    print("1. Check GitHub repository web interface")
    print("2. Verify all files are present")
    print("3. Check commit history")

if __name__ == "__main__":
    main()
