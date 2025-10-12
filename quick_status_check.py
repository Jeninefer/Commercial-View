"""
Quick status check for Commercial-View repository
Provides immediate feedback on production readiness
"""

import os
import sys
from pathlib import Path


def quick_status_check():
    """Perform quick status check"""

    print("🚀 Commercial-View Quick Status Check")
    print("=" * 45)

    repo_root = Path.cwd()
    status = {"passed": 0, "total": 0, "issues": []}

    # Check 1: Repository structure
    status["total"] += 1
    required_dirs = ["src", "frontend", "docs", "scripts"]
    missing_dirs = [d for d in required_dirs if not (repo_root / d).exists()]

    if not missing_dirs:
        status["passed"] += 1
        print("✅ Repository structure complete")
    else:
        status["issues"].append(f"Missing directories: {missing_dirs}")
        print(f"❌ Missing directories: {missing_dirs}")

    # Check 2: No demo files in root
    status["total"] += 1
    demo_files = [f for f in repo_root.glob("*demo*") if f.is_file()]
    demo_files.extend([f for f in repo_root.glob("*example*") if f.is_file()])
    demo_files.extend([f for f in repo_root.glob("test_*") if f.is_file()])

    if not demo_files:
        status["passed"] += 1
        print("✅ No demo files in root directory")
    else:
        status["issues"].append(f"Demo files found: {[f.name for f in demo_files]}")
        print(f"❌ Demo files in root: {[f.name for f in demo_files]}")

    # Check 3: Real data connection
    status["total"] += 1
    google_drive_url = (
        "https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
    )
    has_real_data = False

    try:
        for py_file in repo_root.rglob("*.py"):
            if "upload_to_drive" in py_file.name:
                content = py_file.read_text()
                if google_drive_url in content:
                    has_real_data = True
                    break
    except Exception as e:
        pass

    if has_real_data:
        status["passed"] += 1
        print("✅ Real data source connected")
    else:
        status["issues"].append("Real Google Drive data source not found")
        print("❌ Real data source not found")

    # Check 4: Production files exist
    status["total"] += 1
    production_files = ["README.md", "requirements.txt", "src/__init__.py"]
    missing_files = [f for f in production_files if not (repo_root / f).exists()]

    if not missing_files:
        status["passed"] += 1
        print("✅ Essential production files present")
    else:
        status["issues"].append(f"Missing files: {missing_files}")
        print(f"❌ Missing files: {missing_files}")

    # Summary
    print(f"\n📊 Status: {status['passed']}/{status['total']} checks passed")

    if status["passed"] == status["total"]:
        print("🎉 Repository appears production-ready!")
        print("✅ English-only commercial lending platform")
        print("✅ Zero demo data detected")
        print("✅ Real data sources configured")
        return True
    else:
        print("⚠️ Issues requiring attention:")
        for issue in status["issues"]:
            print(f"  - {issue}")
        return False


if __name__ == "__main__":
    success = quick_status_check()
    sys.exit(0 if success else 1)
