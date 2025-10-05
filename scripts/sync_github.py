"""
GitHub synchronization script for Commercial-View project.

This script handles:
- Git status checking
- Automatic staging of changes
- Commit with meaningful messages
- Push to remote repository
- Branch management
"""

import os
import subprocess
import sys
from datetime import datetime
from typing import List, Tuple, Optional

class GitHubSync:
    """GitHub synchronization manager"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        os.chdir(repo_path)
    
    def run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a git command and return success status and output"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
    
    def get_git_status(self) -> Tuple[List[str], List[str], List[str]]:
        """Get current git status - modified, staged, and untracked files"""
        success, output = self.run_git_command(["git", "status", "--porcelain"])
        if not success:
            return [], [], []
        
        modified = []
        staged = []
        untracked = []
        
        for line in output.split('\n'):
            if line:
                status = line[:2]
                filename = line[3:]
                
                if status.startswith('M') or status.startswith(' M'):
                    modified.append(filename)
                elif status.startswith('A') or status.startswith('D'):
                    staged.append(filename)
                elif status.startswith('??'):
                    untracked.append(filename)
        
        return modified, staged, untracked
    
    def add_files(self, files: List[str] = None) -> bool:
        """Add files to staging area"""
        if files is None:
            # Add all files
            success, _ = self.run_git_command(["git", "add", "."])
        else:
            # Add specific files
            success, _ = self.run_git_command(["git", "add"] + files)
        
        return success
    
    def commit_changes(self, message: Optional[str] = None) -> bool:
        """Commit staged changes"""
        if message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Auto-sync: Update Commercial-View project ({timestamp})"
        
        success, _ = self.run_git_command(["git", "commit", "-m", message])
        return success
    
    def push_changes(self, branch: str = "main") -> bool:
        """Push changes to remote repository"""
        success, _ = self.run_git_command(["git", "push", "origin", branch])
        return success
    
    def get_current_branch(self) -> Optional[str]:
        """Get current branch name"""
        success, output = self.run_git_command(["git", "branch", "--show-current"])
        return output if success else None
    
    def pull_latest(self, branch: str = "main") -> bool:
        """Pull latest changes from remote"""
        success, _ = self.run_git_command(["git", "pull", "origin", branch])
        return success
    
    def create_gitignore_if_missing(self) -> None:
        """Create .gitignore file if it doesn't exist"""
        gitignore_path = ".gitignore"
        if not os.path.exists(gitignore_path):
            gitignore_content = """
# Virtual environments
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Temporary files
*.tmp
get-pip.py

# Google Drive credentials
credentials.json
token.json
drive_config.json

# Export directories (if large)
abaco_runtime/exports/*.csv
abaco_runtime/exports/*.json
abaco_runtime/exports/*.xlsx

# Test artifacts
.pytest_cache/
.coverage
htmlcov/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json
""".strip()
            
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            print("✅ Created .gitignore file")

def main():
    """Main sync function"""
    print("🚀 Commercial-View GitHub Sync")
    print("=" * 40)
    
    # Initialize sync manager
    sync = GitHubSync()
    
    # Create .gitignore if missing
    sync.create_gitignore_if_missing()
    
    # Get current branch
    current_branch = sync.get_current_branch()
    if not current_branch:
        print("❌ Not in a git repository or error getting branch")
        return 1
    
    print(f"📍 Current branch: {current_branch}")
    
    # Check git status
    modified, staged, untracked = sync.get_git_status()
    
    print(f"\n📊 Repository Status:")
    print(f"  📝 Modified files: {len(modified)}")
    print(f"  ✅ Staged files: {len(staged)}")
    print(f"  ❓ Untracked files: {len(untracked)}")
    
    # Show file details
    if modified:
        print(f"\n📝 Modified files:")
        for file in modified:
            print(f"    - {file}")
    
    if untracked:
        print(f"\n❓ Untracked files:")
        for file in untracked:
            print(f"    - {file}")
    
    if not modified and not untracked and not staged:
        print("\n✅ No changes to sync")
        return 0
    
    # Pull latest changes first
    print(f"\n⬇️  Pulling latest changes from origin/{current_branch}...")
    if sync.pull_latest(current_branch):
        print("✅ Successfully pulled latest changes")
    else:
        print("⚠️  Failed to pull changes (continuing anyway)")
    
    # Add all changes
    print(f"\n➕ Adding changes to staging area...")
    if sync.add_files():
        print("✅ Successfully staged all changes")
    else:
        print("❌ Failed to stage changes")
        return 1
    
    # Commit changes
    print(f"\n💾 Committing changes...")
    commit_message = f"Update Commercial-View: sync project files"
    if sync.commit_changes(commit_message):
        print(f"✅ Successfully committed with message: '{commit_message}'")
    else:
        print("❌ Failed to commit changes")
        return 1
    
    # Push changes
    print(f"\n⬆️  Pushing changes to origin/{current_branch}...")
    if sync.push_changes(current_branch):
        print("✅ Successfully pushed changes to GitHub")
    else:
        print("❌ Failed to push changes")
        return 1
    
    print(f"\n🎉 Sync complete! All changes have been pushed to GitHub.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
