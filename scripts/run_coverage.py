#!/usr/bin/env python3
"""
Coverage analysis script for Commercial-View project
"""

import subprocess
import sys
import os
from pathlib import Path

def run_coverage_analysis():
    """Run comprehensive coverage analysis"""
    print("🔍 Running Commercial-View Coverage Analysis")
    print("=" * 50)
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    commands = [
        # Run tests with coverage
        ["coverage", "run", "-m", "pytest", "tests/"],
        # Generate console report
        ["coverage", "report", "-m"],
        # Generate HTML report
        ["coverage", "html"],
        # Generate XML report for CI/CD
        ["coverage", "xml"]
    ]
    
    for cmd in commands:
        print(f"\n🔧 Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
    
    print("\n✅ Coverage analysis completed!")
    print("📊 View HTML report: open htmlcov/index.html")
    return True

if __name__ == "__main__":
    success = run_coverage_analysis()
    sys.exit(0 if success else 1)
