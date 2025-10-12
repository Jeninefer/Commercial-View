"""
Enhanced script to check Git synchronization status and validate Commercial-View project structure
"""

import os
import subprocess
import glob
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


def run_git_command(command: List[str]) -> str:
    """Run git command and return output with enhanced error handling"""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, cwd=os.getcwd()
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def check_project_structure() -> Dict[str, List[str]]:
    """Check comprehensive Commercial-View project structure"""
    project_structure = {
        "core_files": [
            "README.md",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            ".gitignore",
            ".env.example",
        ],
        "application_files": [
            "run.py",
            "server_control.py",
            "src/__init__.py",
            "src/main.py",
            "src/api.py",
            "src/data_loader.py",
        ],
        "commercial_lending_modules": [
            "src/commercial_view/__init__.py",
            "src/commercial_view/pricing/__init__.py",
            "src/commercial_view/pricing/calculator.py",
            "src/commercial_view/dpd/__init__.py",
            "src/commercial_view/dpd/analyzer.py",
            "src/commercial_view/kpi/__init__.py",
            "src/commercial_view/kpi/generator.py",
            "src/commercial_view/risk/__init__.py",
            "src/commercial_view/risk/assessor.py",
            "src/commercial_view/export/__init__.py",
            "src/commercial_view/export/manager.py",
        ],
        "configuration_files": [
            "configs/pricing_config.yml",
            "configs/dpd_policy.yml",
            "configs/column_maps.yml",
        ],
        "data_files": [
            "data/pricing/commercial_loans_pricing.csv",
            "data/pricing/risk_based_pricing.csv",
            "data/pricing/main_pricing.csv",
        ],
        "script_files": [
            "scripts/upload_to_drive.py",
            "scripts/sync_github.py",
            "scripts/uvicorn_manager.py",
            "scripts/activate_project.sh",
            "scripts/activate_project.fish",
            "scripts/activate_project.csh",
            "scripts/Activate-Project.ps1",
        ],
        "frontend_files": [
            "frontend/dashboard/package.json",
            "frontend/dashboard/README.md",
            "frontend/dashboard/src/App.js",
            "frontend/dashboard/public/index.html",
        ],
        "documentation_files": [
            "docs/README.md",
            "docs/versioning.md",
            "docs/performance_slos.md",
            "docs/security_constraints.md",
            "docs/CLOSED_PRS_SUMMARY.md",
        ],
        "export_directories": [
            "abaco_runtime/exports/kpi/json",
            "abaco_runtime/exports/kpi/csv",
            "abaco_runtime/exports/dpd",
            "abaco_runtime/exports/buckets",
        ],
    }

    results = {}
    for category, files in project_structure.items():
        results[category] = {"present": [], "missing": []}

        print(f"\n📁 Checking {category.replace('_', ' ').title()}:")
        for file_path in files:
            if os.path.exists(file_path) or os.path.isdir(file_path):
                print(f"  ✅ {file_path}")
                results[category]["present"].append(file_path)
            else:
                print(f"  ❌ {file_path} - MISSING")
                results[category]["missing"].append(file_path)

    return results


def validate_configuration_files() -> Dict[str, bool]:
    """Validate commercial lending configuration files"""
    print("\n🔍 Validating Configuration Files:")
    validation_results = {}

    config_files = {
        "configs/pricing_config.yml": "Pricing configuration",
        "configs/dpd_policy.yml": "DPD policy configuration",
        "configs/column_maps.yml": "Column mapping configuration",
    }

    for config_path, description in config_files.items():
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    yaml.safe_load(f)
                print(f"  ✅ {description}: Valid YAML")
                validation_results[config_path] = True
            else:
                print(f"  ❌ {description}: File not found")
                validation_results[config_path] = False
        except yaml.YAMLError as e:
            print(f"  ⚠️  {description}: Invalid YAML - {str(e)}")
            validation_results[config_path] = False
        except Exception as e:
            print(f"  ❌ {description}: Error reading file - {str(e)}")
            validation_results[config_path] = False

    return validation_results


def check_git_health() -> Dict[str, str]:
    """Comprehensive Git repository health check"""
    print("\n🔍 Git Repository Health Check:")

    git_info = {}

    # Check if we're in a git repository
    is_git_repo = run_git_command(["git", "rev-parse", "--is-inside-work-tree"])
    git_info["is_git_repo"] = is_git_repo == "true"

    if not git_info["is_git_repo"]:
        print("  ❌ Not in a Git repository")
        return git_info

    # Get current branch
    branch = run_git_command(["git", "branch", "--show-current"])
    git_info["current_branch"] = branch
    print(f"  📍 Current branch: {branch}")

    # Check for uncommitted changes
    status = run_git_command(["git", "status", "--porcelain"])
    git_info["has_changes"] = bool(status.strip())

    if git_info["has_changes"]:
        print("  📊 Uncommitted changes detected:")
        for line in status.split("\n"):
            if line.strip():
                print(f"    {line}")
    else:
        print("  ✅ No uncommitted changes")

    # Check remote repositories
    remotes = run_git_command(["git", "remote", "-v"])
    git_info["remotes"] = remotes
    print("  🔗 Remote repositories:")
    for line in remotes.split("\n"):
        if line.strip():
            print(f"    {line}")

    # Check last commit
    last_commit = run_git_command(["git", "log", "-1", "--oneline"])
    git_info["last_commit"] = last_commit
    print(f"  📝 Last commit: {last_commit}")

    # Check if we're ahead/behind remote
    try:
        ahead_behind = run_git_command(
            ["git", "rev-list", "--left-right", "--count", "HEAD...origin/main"]
        )
        if "Error" not in ahead_behind:
            ahead, behind = ahead_behind.split("\t")
            git_info["commits_ahead"] = int(ahead)
            git_info["commits_behind"] = int(behind)

            if int(ahead) > 0:
                print(f"  ⬆️  {ahead} commits ahead of origin/main")
            if int(behind) > 0:
                print(f"  ⬇️  {behind} commits behind origin/main")
            if int(ahead) == 0 and int(behind) == 0:
                print("  ✅ In sync with origin/main")
    except Exception as e:
        print("  ⚠️  Could not check sync status with remote")

    return git_info


def analyze_project_health() -> Dict[str, any]:
    """Analyze overall Commercial-View project health"""
    print("\n🏥 Project Health Analysis:")

    health_metrics = {
        "python_files": len(glob.glob("**/*.py", recursive=True)),
        "config_files": len(glob.glob("configs/*.yml", recursive=True)),
        "script_files": len(glob.glob("scripts/*.py", recursive=True)),
        "doc_files": len(glob.glob("docs/*.md", recursive=True)),
        "data_files": len(glob.glob("data/**/*.csv", recursive=True)),
        "frontend_components": len(glob.glob("frontend/**/*.js", recursive=True))
        + len(glob.glob("frontend/**/*.jsx", recursive=True)),
        "total_lines_of_code": 0,
    }

    # Count lines of code
    for py_file in glob.glob("**/*.py", recursive=True):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                health_metrics["total_lines_of_code"] += len(f.readlines())
        except Exception as e:
            pass

    print(f"  📊 Python files: {health_metrics['python_files']}")
    print(f"  ⚙️  Configuration files: {health_metrics['config_files']}")
    print(f"  🔧 Script files: {health_metrics['script_files']}")
    print(f"  📚 Documentation files: {health_metrics['doc_files']}")
    print(f"  📈 Data files: {health_metrics['data_files']}")
    print(f"  🖥️  Frontend components: {health_metrics['frontend_components']}")
    print(f"  📝 Total lines of Python code: {health_metrics['total_lines_of_code']:,}")

    return health_metrics


def generate_sync_report(
    project_structure: Dict, git_info: Dict, health_metrics: Dict
) -> None:
    """Generate comprehensive synchronization report"""
    print("\n📋 Synchronization Report")
    print("=" * 50)

    # Calculate missing files
    total_missing = sum(
        len(category["missing"]) for category in project_structure.values()
    )
    total_files = sum(
        len(category["present"]) + len(category["missing"])
        for category in project_structure.values()
    )

    completion_rate = (
        ((total_files - total_missing) / total_files * 100) if total_files > 0 else 0
    )

    print(
        f"📈 Project Completion: {completion_rate:.1f}% ({total_files - total_missing}/{total_files} files)"
    )
    print(
        f"🔍 Repository Status: {'✅ Clean' if not git_info.get('has_changes', True) else '⚠️  Has Changes'}"
    )
    print(f"🌿 Current Branch: {git_info.get('current_branch', 'Unknown')}")

    if total_missing > 0:
        print("\n⚠️  Missing Files by Category:")
        for category, files in project_structure.items():
            if files["missing"]:
                print(
                    f"  📁 {category.replace('_', ' ').title()}: {len(files['missing'])} missing"
                )
                for missing_file in files["missing"][:3]:  # Show first 3
                    print(f"    - {missing_file}")
                if len(files["missing"]) > 3:
                    print(f"    ... and {len(files['missing']) - 3} more")


def suggest_actions(project_structure: Dict, git_info: Dict) -> None:
    """Suggest actions based on project state"""
    print("\n🔧 Recommended Actions:")

    # Check for missing critical files
    critical_missing = []
    for category in ["core_files", "application_files", "configuration_files"]:
        critical_missing.extend(project_structure.get(category, {}).get("missing", []))

    if critical_missing:
        print("1. 🚨 Critical files missing - restore from backup or recreate:")
        for file in critical_missing[:5]:
            print(f"   - {file}")

    # Git-specific suggestions
    if git_info.get("has_changes", False):
        print("2. 📝 Commit uncommitted changes:")
        print("   git add .")
        print("   git commit -m 'Sync Commercial-View project structure'")

    if git_info.get("commits_ahead", 0) > 0:
        print("3. ⬆️  Push local commits to remote:")
        print("   git push origin main")

    if git_info.get("commits_behind", 0) > 0:
        print("4. ⬇️  Pull latest changes from remote:")
        print("   git pull origin main")

    # Project-specific suggestions
    print("5. 🔍 Validate project setup:")
    print("   python scripts/check_sync_status.py")
    print("6. 🧪 Run tests to ensure functionality:")
    print("   pytest tests/")
    print("7. 📚 Update documentation if needed")
    print("8. 🔄 Consider running full project validation")


def main():
    """Main execution function with comprehensive Commercial-View project analysis"""
    print("🏦 Commercial-View Synchronization Status Check")
    print("=" * 60)
    print(f"⏰ Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Check project structure
        project_structure = check_project_structure()

        # Validate configuration files
        config_validation = validate_configuration_files()

        # Check Git health
        git_info = check_git_health()

        # Analyze project health
        health_metrics = analyze_project_health()

        # Generate comprehensive report
        generate_sync_report(project_structure, git_info, health_metrics)

        # Provide actionable suggestions
        suggest_actions(project_structure, git_info)

        print("\n✅ Analysis completed successfully!")
        print("💡 For detailed project setup, see: setup_guide.ipynb")
        print("📚 For documentation, see: docs/README.md")

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print(
            "Please ensure you're running this script from the project root directory"
        )


if __name__ == "__main__":
    main()
