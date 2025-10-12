"""
Simple runner for the complete Abaco production test
Ensures proper setup and runs the comprehensive test
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the Abaco production test based on exact 48,853 record schema."""
    
    print("🏦 Abaco Production Test Runner")
    print("=" * 35)
    
    # Fix SonarLint issues - replace f-strings without variables
    project_root = Path(__file__).parent
    print("📁 Project root: " + str(project_root))
    
    # Check for key files
    key_files = [
        'src/data_loader.py',
        'src/abaco_schema.py',
        'config'
    ]
    
    missing_files = []
    for file_path in key_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ Key files present")
    
    # Run the comprehensive test
    test_script = project_root / 'scripts' / 'complete_abaco_integration_test.py'
    
    if test_script.exists():
        print("🚀 Running comprehensive Abaco test...")
        result = subprocess.run([sys.executable, str(test_script)], 
                              capture_output=False, text=True)
        return result.returncode == 0
    else:
        print(f"❌ Test script not found: {test_script}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("✅ Test runner completed successfully")
    else:
        print("❌ Test runner failed - check output above")

    sys.exit(0 if success else 1)
