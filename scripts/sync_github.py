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
    
    def add_files(self, files: Optional[List[str]] = None) -> bool:
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
    
    def validate_git_repository(self) -> Optional[str]:
        """Validate git repository and return current branch"""
        current_branch = self.get_current_branch()
        if not current_branch:
            print("❌ Not in a git repository or error getting branch")
            return None
        return current_branch
    
    def display_repository_status(self, modified: List[str], staged: List[str], untracked: List[str]) -> None:
        """Display current repository status"""
        print("📊 Repository Status:")
        print(f"  📝 Modified files: {len(modified)}")
        print(f"  ✅ Staged files: {len(staged)}")
        print(f"  ❓ Untracked files: {len(untracked)}")
        
        if modified:
            print("📝 Modified files:")
            for file in modified:
                print(f"    - {file}")
        
        if untracked:
            print("❓ Untracked files:")
            for file in untracked:
                print(f"    - {file}")
    
    def has_changes_to_sync(self, modified: List[str], staged: List[str], untracked: List[str]) -> bool:
        """Check if there are any changes to sync"""
        return bool(modified or untracked or staged)
    
    def sync_with_remote(self, branch: str) -> bool:
        """Pull latest changes from remote"""
        print(f"⬇️  Pulling latest changes from origin/{branch}...")
        if self.pull_latest(branch):
            print("✅ Successfully pulled latest changes")
            return True
        else:
            print("⚠️  Failed to pull changes (continuing anyway)")
            return False
    
    def stage_all_changes(self) -> bool:
        """Stage all changes for commit"""
        print("➕ Adding changes to staging area...")
        if self.add_files():
            print("✅ Successfully staged all changes")
            return True
        else:
            print("❌ Failed to stage changes")
            return False
    
    def commit_and_push_changes(self, branch: str) -> bool:
        """Commit and push changes to remote"""
        # Commit changes
        print("💾 Committing changes...")
        commit_message = "Update Commercial-View: sync project files"
        if not self.commit_changes(commit_message):
            print("❌ Failed to commit changes")
            return False
        
        print(f"✅ Successfully committed with message: '{commit_message}'")
        
        # Push changes
        print(f"⬆️  Pushing changes to origin/{branch}...")
        if not self.push_changes(branch):
            print("❌ Failed to push changes")
            return False
        
        print("✅ Successfully pushed changes to GitHub")
        return True
    
    def perform_sync(self) -> int:
        """Perform the complete sync operation"""
        # Validate repository
        current_branch = self.validate_git_repository()
        if not current_branch:
            return 1
        
        print(f"📍 Current branch: {current_branch}")
        
        # Get repository status
        modified, staged, untracked = self.get_git_status()
        self.display_repository_status(modified, staged, untracked)
        
        # Check if there are changes to sync
        if not self.has_changes_to_sync(modified, staged, untracked):
            print("✅ No changes to sync")
            return 0
        
        # Sync with remote
        self.sync_with_remote(current_branch)
        
        # Stage changes
        if not self.stage_all_changes():
            return 1
        
        # Commit and push changes
        if not self.commit_and_push_changes(current_branch):
            return 1
        
        print("🎉 Sync complete! All changes have been pushed to GitHub.")
        return 0

def main():
    """Main sync function"""
    print("🚀 Commercial-View GitHub Sync")
    print("=" * 40)
    
    # Initialize sync manager
    sync = GitHubSync()
    
    # Create .gitignore if missing
    sync.create_gitignore_if_missing()
    
    # Perform sync operation
    return sync.perform_sync()

if __name__ == "__main__":
    sys.exit(main())
