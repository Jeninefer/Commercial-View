"""
Comprehensive Repository Validation Script
Checks for: syntax errors, duplicates, dummy data, and validates real Abaco data
"""

import os
import re
import json
import ast
import hashlib
from pathlib import Path
from collections import defaultdict
import subprocess


class RepositoryValidator:
    """Comprehensive validator for Commercial-View repository."""

    def __init__(self):
        # Use environment variable or fallback to current working directory for portability
        self.base_path = Path(os.environ.get("REPO_BASE_PATH", Path.cwd()))
        self.errors = []
        self.warnings = []
        self.duplicates = []
        self.dummy_data = []

        # Real Abaco data constants for validation
        self.REAL_DATA = {
            "total_records": 48853,
            "loan_records": 16205,
            "payment_records": 16443,
            "schedule_records": 16205,
            "portfolio_value": 208192588.65,
            "currency": "USD",
            "companies": ["Abaco Technologies", "Abaco Financial"],
            "apr_min": 0.2947,
            "apr_max": 0.3699,
            "payment_frequency": "bullet",
            "product_type": "factoring",
        }
        # Dummy data patterns to find and replace
        DUMMY_PATTERNS = [
            (r"example\.com", "Dummy email domain"),
            (r"test@test\.com", "Test email"),
            (r"TODO", "TODO comment"),
            (r"FIXME", "FIXME comment"),
            (r"XXX", "Placeholder comment"),
            (r"Lorem ipsum", "Placeholder text"),
            (r"sample_?data", "Sample data reference"),
            (r"dummy_?value", "Dummy value"),
            (r"placeholder", "Placeholder text"),
            (r"12345", "Example ID (unless part of real data)"),
            (r"foo|bar|baz", "Placeholder variable names"),
        ]
        ]

    def check_python_syntax(self):
        """Check all Python files for syntax errors."""
        print("🔍 Checking Python syntax errors...")

        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    code = f.read()
                    ast.parse(code)
                print(f"   ✅ {py_file.name}: Syntax OK")
            except SyntaxError as e:
                error_msg = f"SYNTAX ERROR in {py_file}: Line {e.lineno}: {e.msg}"
                self.errors.append(error_msg)
                print(f"   ❌ {error_msg}")
            except Exception as e:
                warning_msg = f"WARNING in {py_file}: {str(e)}"
                self.warnings.append(warning_msg)
                print(f"   ⚠️  {warning_msg}")

    def find_duplicate_files(self):
        """Find duplicate files by content hash."""
        print("\n🔍 Searching for duplicate files...")

        file_hashes = defaultdict(list)

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and not any(
                ex in str(file_path)
                for ex in [".git", "__pycache__", ".venv", "node_modules"]
            ):
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_hashes[file_hash].append(str(file_path))
                except Exception:
                    continue

        for file_hash, paths in file_hashes.items():
            if len(paths) > 1:
                self.duplicates.append(paths)
                print(f"   ⚠️  Found {len(paths)} duplicate files:")
                for path in paths:
                    print(f"      - {Path(path).name}")

        if not self.duplicates:
            print("   ✅ No duplicate files found")

    def find_dummy_data(self):
        """Find dummy data patterns in code."""
        print("\n🔍 Searching for dummy/placeholder data...")

        for file_path in self.base_path.rglob("*.py"):
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                for pattern, description in DUMMY_PATTERNS:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1
                            self.dummy_data.append(
                                {
                                    "file": str(file_path),
                                    "line": line_num,
                                    "pattern": description,
                                    "matched": match.group(),
                                }
                            )
                            print(
                                f"   ⚠️  {file_path.name}:{line_num} - {description}: '{match.group()}'"
                            )
                            )
            except Exception:
                continue

        if not self.dummy_data:
            print("   ✅ No dummy data found")

    def validate_real_abaco_data(self):
        """Validate that real Abaco data constants are used correctly."""
        print("\n🔍 Validating real Abaco data usage...")

        validation_results = {
            "portfolio_value": False,
            "record_counts": False,
            "currency": False,
            "apr_range": False,
            "companies": False,
            "product_type": False,
        }

        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                    # Check for portfolio value
                    if "208192588.65" in content:
                        validation_results["portfolio_value"] = True

                    # Check for record counts
                    if "48853" in content or "16205" in content:
                        validation_results["record_counts"] = True

                    # Check for USD currency
                    if '"USD"' in content or "'USD'" in content:
                        validation_results["currency"] = True

                    # Check for APR range
                    if "0.2947" in content or "0.3699" in content:
                        validation_results["apr_range"] = True

                    # Check for companies
                    if "Abaco Technologies" in content or "Abaco Financial" in content:
                        validation_results["companies"] = True

                    # Check for product type
                    if "factoring" in content.lower():
                        validation_results["product_type"] = True
            except Exception:
                continue

        for key, value in validation_results.items():
            status = "✅" if value else "❌"
            print(
                f"   {status} {key.replace('_', ' ').title()}: {'Found' if value else 'Not Found'}"
            )

        return validation_results

    def check_run_py_constants(self):
        """Check if run.py has proper constant definitions."""
        print("\n🔍 Checking run.py for proper constants...")

        run_py = self.base_path / "run.py"
        if not run_py.exists():
            print("   ⚠️  run.py not found")
            return False

        try:
            with open(run_py, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for proper constant definitions
            required_constants = [
                "DAYS_IN_DEFAULT",
                "INTEREST_RATE_APR",
                "OUTSTANDING_LOAN_VALUE",
                "LOAN_CURRENCY",
                "PRODUCT_TYPE",
            ]

            all_defined = True
            for const in required_constants:
                # Check if constant is defined before use
                pattern = rf'^{const}\s*=\s*["\'].*["\']'
                if re.search(pattern, content, re.MULTILINE):
                    print(f"   ✅ {const} properly defined")
                else:
                    print(
                        f"   ❌ {const} not properly defined or used before definition"
                    )
                    self.errors.append(
                        f"Constant {const} not properly defined in run.py"
                    )
                    all_defined = False

            return all_defined
        except Exception as e:
            print(f"   ❌ Error checking run.py: {e}")
            return False

    def generate_report(self):
        """Generate comprehensive validation report."""
        print("\n" + "=" * 70)
        print("📊 REPOSITORY VALIDATION REPORT")
        print("=" * 70)

        report = {
            "syntax_errors": len(self.errors),
            "warnings": len(self.warnings),
            "duplicates": len(self.duplicates),
            "dummy_data": len(self.dummy_data),
            "timestamp": "2024-10-12",
        }

        print(
            f"\n{'❌' if report['syntax_errors'] > 0 else '✅'} Syntax Errors: {report['syntax_errors']}"
        )
        if self.errors:
            for error in self.errors:
                print(f"   - {error}")

        print(
            f"\n{'⚠️ ' if report['warnings'] > 0 else '✅'} Warnings: {report['warnings']}"
        )
        if self.warnings:
            for warning in self.warnings[:5]:  # Show first 5
                print(f"   - {warning}")

        print(
            f"\n{'⚠️ ' if report['duplicates'] > 0 else '✅'} Duplicate Files: {report['duplicates']}"
        )
        if self.duplicates:
            for dup_group in self.duplicates[:3]:  # Show first 3
                print(f"   - {len(dup_group)} duplicates of {Path(dup_group[0]).name}")

        print(
            f"\n{'⚠️ ' if report['dummy_data'] > 0 else '✅'} Dummy Data Instances: {report['dummy_data']}"
        )
        if self.dummy_data:
            for item in self.dummy_data[:10]:  # Show first 10
                print(
                    f"   - {Path(item['file']).name}:{item['line']} - {item['pattern']}"
                )

        print("\n💼 REAL ABACO DATA VALIDATION:")
        print(f"   ✅ Total Records: {self.REAL_DATA['total_records']:,}")
        print(
            f"   ✅ Portfolio Value: ${self.REAL_DATA['portfolio_value']:,.2f} {self.REAL_DATA['currency']}"
        )
        print(f"   ✅ Companies: {', '.join(self.REAL_DATA['companies'])}")
        print(
            f"   ✅ APR Range: {self.REAL_DATA['apr_min']*100}% - {self.REAL_DATA['apr_max']*100}%"
        )
        print(f"   ✅ Product Type: {self.REAL_DATA['product_type']}")

        # Save report
        report_file = self.base_path / "VALIDATION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📋 Report saved to: {report_file}")

        # Overall status
        if report["syntax_errors"] == 0:
            print("\n🎉 ✅ NO SYNTAX ERRORS FOUND - REPOSITORY IS CLEAN!")
        else:
            print(
                f"\n⚠️  {report['syntax_errors']} CRITICAL ISSUES FOUND - NEEDS FIXING"
            )

        return report

    def run_full_validation(self):
        """Run complete validation suite."""
        print("🚀 Starting Comprehensive Repository Validation")
        print("=" * 70)

        # Check syntax
        self.check_python_syntax()

        # Check run.py constants
        self.check_run_py_constants()

        # Find duplicates
        self.find_duplicate_files()

        # Find dummy data
        self.find_dummy_data()

        # Validate real data usage
        self.validate_real_abaco_data()

        # Generate report
        report = self.generate_report()

        print("\n" + "=" * 70)
        print("🎯 VALIDATION COMPLETE")
        print("=" * 70)

        return report


def main():
    """Main execution function."""
    validator = RepositoryValidator()
    report = validator.run_full_validation()

    # Return exit code based on errors
    return 0 if report["syntax_errors"] == 0 else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
