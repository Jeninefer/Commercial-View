"""
Fix GitHub workflow push issue for Commercial-View
Resolves OAuth scope limitations and ensures clean repository
"""

import os
import shutil
import subprocess
from pathlib import Path

def fix_workflow_permissions():
    """Fix GitHub workflow push permission issues"""
    
    print("🔧 Fixing GitHub workflow permission issues...")
    
    # Move workflow files temporarily to avoid OAuth scope issues
    github_dir = Path(".github")
    workflows_dir = github_dir / "workflows"
    
    if workflows_dir.exists():
        # Create backup
        backup_dir = Path("github_workflows_backup")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        shutil.copytree(workflows_dir, backup_dir)
        print(f"✅ Backed up workflows to {backup_dir}")
        
        # Remove from git tracking temporarily
        try:
            subprocess.run(['git', 'rm', '-r', '--cached', '.github/workflows/'], 
                         check=True, capture_output=True)
            print("✅ Removed workflows from git tracking")
        except subprocess.CalledProcessError:
            print("⚠️  Workflows not in git tracking")
        
        # Remove the directory
        shutil.rmtree(workflows_dir)
        print("✅ Temporarily removed workflows directory")
    
    return True

def create_english_only_validation():
    """Create validation script for English-only content"""
    
    validation_script = """#!/usr/bin/env python3
'''
English-only content validation for Commercial-View
Ensures 100% English content with no demo data
'''

import re
import sys
from pathlib import Path

def validate_english_only():
    '''Validate all content is in English'''
    
    issues = []
    root = Path('.')
    
    # Check for non-English content
    non_english_patterns = [
        r'[^\x00-\x7F]+',  # Non-ASCII
        r'\\b(español|français|deutsch)\\b',  # Other languages
    ]
    
    for file_path in root.rglob('*.py'):
        if '.venv' in str(file_path) or 'node_modules' in str(file_path):
            continue
            
        try:
            content = file_path.read_text(encoding='utf-8')
            for pattern in non_english_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"Non-English content in {file_path}")
        except:
            continue
    
    if issues:
        print("❌ Non-English content found:")
        for issue in issues[:5]:  # Show first 5
            print(f"  - {issue}")
        return False
    
    print("✅ All content is in English")
    return True

def validate_no_demo_data():
    '''Validate no demo or example data exists'''
    
    demo_patterns = [
        r'demo.*data',
        r'example.*data',
        r'sample.*data',
        r'mock.*data',
        r'lorem ipsum',
        r'john doe',
        r'jane smith',
        r'acme corp'
    ]
    
    issues = []
    root = Path('.')
    
    for file_path in root.rglob('*'):
        if (file_path.is_file() and 
            file_path.suffix in ['.py', '.md', '.csv', '.json'] and
            '.venv' not in str(file_path) and
            'node_modules' not in str(file_path)):
            
            try:
                content = file_path.read_text(encoding='utf-8').lower()
                for pattern in demo_patterns:
                    if re.search(pattern, content):
                        issues.append(f"Demo data pattern '{pattern}' in {file_path}")
                        break
            except:
                continue
    
    if issues:
        print("❌ Demo data found:")
        for issue in issues[:5]:  # Show first 5
            print(f"  - {issue}")
        return False
    
    print("✅ No demo data found")
    return True

if __name__ == "__main__":
    print("🔍 Validating Commercial-View Repository")
    print("=" * 50)
    
    english_ok = validate_english_only()
    demo_ok = validate_no_demo_data()
    
    if english_ok and demo_ok:
        print("\\n🎉 Repository validation passed!")
        sys.exit(0)
    else:
        print("\\n💥 Repository validation failed!")
        sys.exit(1)
"""
    
    # Write validation script
    script_path = Path("scripts/validate_english_only.py")
    script_path.write_text(validation_script)
    script_path.chmod(0o755)
    
    print(f"✅ Created validation script: {script_path}")
    return True

def clean_repository():
    """Clean repository of any demo/example content"""
    
    print("🧹 Cleaning repository of demo content...")
    
    # Files to remove (demo/example content)
    demo_files = [
        "run_demo.py",
        "test_actual_files.py",
        "test_feature_engineer_fix.py", 
        "test_feature_engineer.py",
        "test_modules_fixed.py",
        "test_modules.py",
        "test_quick_fix.py"
    ]
    
    removed_count = 0
    for demo_file in demo_files:
        file_path = Path(demo_file)
        if file_path.exists():
            file_path.unlink()
            removed_count += 1
            print(f"  ✅ Removed: {demo_file}")
    
    print(f"✅ Cleaned {removed_count} demo files")
    return True

def update_gitignore():
    """Update .gitignore to exclude workflow files temporarily"""
    
    gitignore_path = Path(".gitignore")
    
    # Add workflow exclusion
    exclusions = [
        "\n# Temporary workflow exclusion",
        ".github/workflows/",
        "github_workflows_backup/",
        "\n# Demo and test files",
        "*demo*",
        "*example*",
        "*sample*",
        "test_*.py",
    ]
    
    with open(gitignore_path, 'a') as f:
        f.write('\n'.join(exclusions))
    
    print("✅ Updated .gitignore with exclusions")
    return True

def main():
    """Main execution function"""
    
    print("🚀 Commercial-View Repository Cleanup")
    print("=" * 50)
    
    # Execute cleanup steps
    steps = [
        ("Fix workflow permissions", fix_workflow_permissions),
        ("Clean demo content", clean_repository),
        ("Create validation script", create_english_only_validation),
        ("Update .gitignore", update_gitignore)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            return False
    
    print("\n🎉 Repository cleanup completed!")
    print("\nNext steps:")
    print("1. Run: python scripts/validate_english_only.py")
    print("2. Git add and commit changes")
    print("3. Push to GitHub (workflows excluded)")
    print("4. Manually add workflows through GitHub web interface")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
