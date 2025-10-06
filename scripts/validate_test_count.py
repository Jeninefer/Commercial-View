"""
Validate that 31+ test cases are executed in the test suite
Part of CI/CD quality gates for Commercial-View
"""

import argparse
import sys
import subprocess
import json
import re


def count_test_cases():
    """Count total test cases across the test suite"""

    # Run pytest with json report
    result = subprocess.run(
        [
            "pytest",
            "tests/",
            "--collect-only",
            "--quiet",
            "--json-report",
            "--json-report-file=/tmp/test_report.json",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ Failed to collect tests: {result.stderr}")
        return 0

    try:
        with open("/tmp/test_report.json", "r") as f:
            report = json.load(f)

        test_count = len(report.get("tests", []))
        return test_count
    except Exception as e:
        print(f"❌ Failed to parse test report: {e}")
        return 0


def validate_test_categories():
    """Validate specific test categories exist"""
    categories = {
        "KPI Engine Tests": "tests/test_kpi_engine.py",
        "Data Pipeline Tests": "tests/test_data_pipeline.py",
        "API Endpoint Tests": "tests/test_api_endpoints.py",
        "Dashboard Tests": "frontend/src/components/__tests__/Dashboard.test.tsx",
        "AI Integration Tests": "tests/test_ai_integrations.py",
    }

    missing_categories = []
    for category, file_path in categories.items():
        try:
            with open(file_path, "r") as f:
                content = f.read()
                # Count test functions/cases
                test_functions = len(re.findall(r"(def test_|test\()", content))
                if test_functions == 0:
                    missing_categories.append(category)
                else:
                    print(f"✅ {category}: {test_functions} test cases found")
        except FileNotFoundError:
            missing_categories.append(category)
            print(f"❌ {category}: File not found - {file_path}")

    return missing_categories


def main():
    parser = argparse.ArgumentParser(description="Validate test suite completeness")
    parser.add_argument(
        "--minimum", type=int, default=31, help="Minimum number of test cases required"
    )
    args = parser.parse_args()

    print(f"🧪 Validating Commercial-View Test Suite (minimum: {args.minimum} cases)")
    print("=" * 60)

    # Count total test cases
    total_tests = count_test_cases()
    print(f"\n📊 Total test cases found: {total_tests}")

    # Validate test categories
    missing_categories = validate_test_categories()

    # Final validation
    success = True

    if total_tests < args.minimum:
        print(f"❌ Insufficient test cases: {total_tests} < {args.minimum}")
        success = False
    else:
        print(f"✅ Test count meets requirement: {total_tests} >= {args.minimum}")

    if missing_categories:
        print(f"❌ Missing test categories: {missing_categories}")
        success = False
    else:
        print("✅ All required test categories present")

    if success:
        print("\n🎉 Test suite validation passed!")
        sys.exit(0)
    else:
        print("\n💥 Test suite validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
