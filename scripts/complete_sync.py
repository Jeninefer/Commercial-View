"""
Enhanced complete synchronization script for Commercial-View commercial lending project
"""

import os
import subprocess
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

def run_command(command: List[str], check: bool = True, cwd: Optional[str] = None) -> Tuple[bool, str]:
    """Run command and return result with enhanced error handling"""
    print(f"🔧 Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=check,
            cwd=cwd or os.getcwd()
        )
        if result.stdout.strip():
            print(f"✅ Output: {result.stdout.strip()}")
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else f"Command failed with exit code {e.returncode}"
        print(f"❌ Error: {error_msg}")
        return False, error_msg
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, str(e)

def validate_project_structure() -> Dict[str, List[str]]:
    """Validate Commercial-View project structure before sync"""
    print("\n🔍 Validating Commercial-View Project Structure...")
    
    critical_files = [
        "README.md",
        "requirements.txt", 
        "run.py",
        "server_control.py",
        "src/main.py",
        "configs/pricing_config.yml",
        "configs/dpd_policy.yml",
        "configs/column_maps.yml"
    ]
    
    important_directories = [
        "src/commercial_view",
        "scripts",
        "configs",
        "data/pricing",
        "frontend/dashboard",
        "docs",
        "abaco_runtime/exports"
    ]
    
    validation_results = {"missing_files": [], "missing_dirs": [], "present": []}
    
    # Check critical files
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
            validation_results["present"].append(file_path)
        else:
            print(f"  ❌ {file_path} - MISSING")
            validation_results["missing_files"].append(file_path)
    
    # Check important directories
    for dir_path in important_directories:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"  ✅ {dir_path}/")
            validation_results["present"].append(dir_path)
        else:
            print(f"  ❌ {dir_path}/ - MISSING")
            validation_results["missing_dirs"].append(dir_path)
    
    return validation_results

def create_backup() -> Optional[str]:
    """Create backup of critical files before sync"""
    print("\n💾 Creating Backup...")
    
    backup_dir = f"backups/sync_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup critical files
        critical_paths = ["configs", "src", "scripts", "data"]
        
        for path in critical_paths:
            if os.path.exists(path):
                dest_path = os.path.join(backup_dir, path)
                if os.path.isdir(path):
                    shutil.copytree(path, dest_path, ignore_errors=True)
                else:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(path, dest_path)
                print(f"  ✅ Backed up: {path}")
        
        print(f"  💾 Backup created: {backup_dir}")
        return backup_dir
    
    except Exception as e:
        print(f"  ⚠️  Backup failed: {str(e)}")
        return None

def check_git_repository() -> Dict[str, any]:
    """Enhanced Git repository validation"""
    print("\n🔍 Validating Git Repository...")
    
    git_info = {}
    
    # Check if we're in a git repository
    success, output = run_command(["git", "rev-parse", "--is-inside-work-tree"], check=False)
    git_info["is_repo"] = success and output == "true"
    
    if not git_info["is_repo"]:
        print("  ❌ Not in a Git repository")
        return git_info
    
    # Get repository information
    success, branch = run_command(["git", "branch", "--show-current"], check=False)
    git_info["current_branch"] = branch if success else "unknown"
    
    success, remote_url = run_command(["git", "remote", "get-url", "origin"], check=False)
    git_info["remote_url"] = remote_url if success else "no remote"
    
    success, status = run_command(["git", "status", "--porcelain"], check=False)
    git_info["has_changes"] = bool(status.strip()) if success else False
    git_info["status_output"] = status if success else ""
    
    # Check if we can connect to remote
    success, _ = run_command(["git", "ls-remote", "--heads", "origin"], check=False)
    git_info["remote_accessible"] = success
    
    print(f"  📍 Branch: {git_info['current_branch']}")
    print(f"  🔗 Remote: {git_info['remote_url']}")
    print(f"  📊 Changes: {'Yes' if git_info['has_changes'] else 'No'}")
    print(f"  🌐 Remote accessible: {'Yes' if git_info['remote_accessible'] else 'No'}")
    
    return git_info

def analyze_changes() -> Dict[str, List[str]]:
    """Analyze what changes will be committed"""
    print("\n📊 Analyzing Changes...")
    
    changes = {"modified": [], "added": [], "deleted": [], "untracked": []}
    
    success, status_output = run_command(["git", "status", "--porcelain"], check=False)
    
    if not success:
        return changes
    
    for line in status_output.split('\n'):
        if not line.strip():
            continue
            
        status_code = line[:2]
        filename = line[3:].strip()
        
        if status_code.startswith('M'):
            changes["modified"].append(filename)
        elif status_code.startswith('A'):
            changes["added"].append(filename)
        elif status_code.startswith('D'):
            changes["deleted"].append(filename)
        elif status_code.startswith('??'):
            changes["untracked"].append(filename)
    
    # Display changes summary
    for change_type, files in changes.items():
        if files:
            print(f"  📝 {change_type.title()}: {len(files)} files")
            for file in files[:5]:  # Show first 5 files
                print(f"    - {file}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
    
    return changes

def perform_intelligent_commit(changes: Dict[str, List[str]]) -> bool:
    """Create intelligent commit message based on changes"""
    print("\n📝 Creating Intelligent Commit...")
    
    # Generate commit message based on changes
    commit_parts = []
    
    if changes["added"]:
        commit_parts.append(f"Add {len(changes['added'])} new files")
    if changes["modified"]:
        commit_parts.append(f"Update {len(changes['modified'])} files")
    if changes["deleted"]:
        commit_parts.append(f"Remove {len(changes['deleted'])} files")
    
    if not commit_parts:
        print("  ℹ️  No changes to commit")
        return False
    
    # Create detailed commit message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base_msg = "Commercial-View: " + ", ".join(commit_parts)
    detailed_msg = f"{base_msg}\n\nSync performed: {timestamp}\nTotal changes: {sum(len(files) for files in changes.values())}"
    
    success, _ = run_command(["git", "commit", "-m", detailed_msg], check=False)
    
    return success

def sync_with_remote(git_info: Dict[str, any]) -> bool:
    """Enhanced remote synchronization"""
    print("\n🔄 Synchronizing with Remote...")
    
    if not git_info.get("remote_accessible", False):
        print("  ❌ Cannot access remote repository")
        return False
    
    # Fetch latest changes
    print("  📥 Fetching latest changes...")
    success, _ = run_command(["git", "fetch", "origin"], check=False)
    
    if not success:
        print("  ⚠️  Failed to fetch from remote")
    
    # Check if we're behind
    success, behind_output = run_command(
        ["git", "rev-list", "--count", "HEAD..origin/main"], 
        check=False
    )
    
    if success and behind_output.isdigit() and int(behind_output) > 0:
        print(f"  ⬇️  {behind_output} commits behind remote")
        print("  🔄 Consider pulling latest changes first")
    
    # Push changes
    print("  ⬆️  Pushing to remote...")
    success, output = run_command(["git", "push", "origin", "main"], check=False)
    
    if success:
        print("  ✅ Successfully pushed to remote")
        return True
    else:
        print("  ❌ Failed to push to remote")
        print("  💡 Try: git pull origin main && git push origin main")
        return False

def generate_sync_report(validation_results: Dict, git_info: Dict, backup_path: Optional[str]) -> None:
    """Generate comprehensive sync report"""
    print("\n📋 Sync Report")
    print("=" * 50)
    
    # Project validation summary
    total_missing = len(validation_results.get("missing_files", [])) + len(validation_results.get("missing_dirs", []))
    total_present = len(validation_results.get("present", []))
    
    print(f"📊 Project Structure: {total_present} items present, {total_missing} missing")
    print(f"🔗 Git Repository: {git_info.get('current_branch', 'unknown')} branch")
    print(f"🌐 Remote Access: {'✅' if git_info.get('remote_accessible', False) else '❌'}")
    print(f"💾 Backup Created: {'✅' if backup_path else '❌'}")
    
    if backup_path:
        print(f"💾 Backup Location: {backup_path}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if total_missing > 0:
        print("  1. Restore missing files from backup or repository")
    if not git_info.get("remote_accessible", False):
        print("  2. Check network connection and Git credentials")
    print("  3. Verify sync on GitHub web interface")
    print("  4. Run tests to ensure functionality")

def main():
    """Enhanced main sync function with comprehensive Commercial-View project management"""
    print("🏦 Commercial-View Enhanced Complete Sync")
    print("=" * 60)
    print(f"⏰ Sync started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Validate environment
        print(f"\n📍 Working Directory: {os.getcwd()}")
        if not os.path.exists(".git"):
            print("❌ Not in a Git repository root. Please run from project root.")
            sys.exit(1)
        
        # Step 2: Validate project structure
        validation_results = validate_project_structure()
        
        # Step 3: Create backup
        backup_path = create_backup()
        
        # Step 4: Check Git repository
        git_info = check_git_repository()
        
        if not git_info.get("is_repo", False):
            print("❌ Git repository validation failed")
            sys.exit(1)
        
        # Step 5: Add all files with validation
        print("\n📁 Staging Files...")
        run_command(["git", "add", "."])
        run_command(["git", "add", "-A"])  # Include deletions
        
        # Step 6: Analyze changes
        changes = analyze_changes()
        
        # Step 7: Create intelligent commit
        if any(changes.values()):
            commit_success = perform_intelligent_commit(changes)
            
            if commit_success:
                print("  ✅ Commit created successfully")
            else:
                print("  ⚠️  Commit failed or no changes")
        else:
            print("  ℹ️  No changes to commit")
            commit_success = False
        
        # Step 8: Sync with remote
        if commit_success or git_info.get("has_changes", False):
            sync_success = sync_with_remote(git_info)
        else:
            sync_success = True
            print("  ℹ️  No sync needed")
        
        # Step 9: Final status check
        print("\n🔍 Final Status Check...")
        run_command(["git", "status"], check=False)
        
        # Step 10: Generate report
        generate_sync_report(validation_results, git_info, backup_path)
        
        # Final result
        if sync_success:
            print(f"\n🎉 Commercial-View sync completed successfully!")
        else:
            print(f"\n⚠️  Sync completed with warnings")
        
        print(f"\n📚 Next Steps:")
        print("1. Verify changes on GitHub web interface")
        print("2. Run: python scripts/check_sync_status.py")
        print("3. Test application: python run.py")
        print("4. Review documentation: docs/README.md")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during sync: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
