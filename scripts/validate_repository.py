"""Comprehensive Repository Validation Script

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
            "product_type": "factoring",
            "apr_range": {"min": 0.2947, "max": 0.3699},
        }
<<<<<<< Updated upstream
        # Dummy data patterns to find and replace
        self.DUMMY_PATTERNS = [
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
=======

    def validate_all(self):
        """Run all validation checks."""
        print("🔍 Starting comprehensive repository validation...")

        self.check_python_syntax()
        self.find_duplicates()
        self.check_dummy_data()
        self.validate_abaco_data()

        return self.generate_report()
>>>>>>> Stashed changes

    def check_python_syntax(self):
        """Check all Python files for syntax errors."""
        print("\n🐍 Checking Python syntax...")

        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print(f"   ✅ {py_file.name}: Syntax OK")
                else:
                    error_msg = f"SYNTAX ERROR in {py_file}: {result.stderr}"
                    self.errors.append(error_msg)
                    print(f"   ❌ {py_file.name}: Syntax error")
            except Exception as e:
                self.errors.append(f"Error checking {py_file}: {e}")

    def find_duplicates(self):
        """Find duplicate files by content hash."""
        print("\n🔍 Searching for duplicate files...")

        file_hashes = defaultdict(list)

        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and ".venv" not in str(file_path):
                try:
                    content_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
                    file_hashes[content_hash].append(file_path.name)
                except Exception:
                    continue

        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.duplicates.append(files)
                print(f"   ⚠️  Found {len(files)} duplicate files:")
                for f in files:
                    print(f"      - {f}")

    def check_dummy_data(self):
        """Check for placeholder/dummy data."""
        print("\n🔍 Searching for dummy/placeholder data...")

<<<<<<< Updated upstream
        for file_path in self.base_path.rglob("*.py"):
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                for pattern, description in self.DUMMY_PATTERNS:
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
=======
        dummy_patterns = [
            (r"TODO", "TODO comment"),
            (r"FIXME", "FIXME comment"),
            (r"XXX", "Placeholder comment"),
            (r"Lorem ipsum", "Placeholder text"),
            (r"placeholder", "Placeholder text"),
            (r"sample_data", "Sample data reference"),
            (r"12345", "Example ID (unless part of real data)"),
            (r"\bfoo\b|\bbar\b|\bbaz\b", "Placeholder variable names"),
        ]
>>>>>>> Stashed changes

        for py_file in self.base_path.rglob("*.py"):
            if ".venv" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                for pattern, description in dummy_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        self.dummy_data.append(
                            {
                                "file": py_file.name,
                                "line": line_num,
                                "type": description,
                                "text": match.group(),
                            }
                        )
                        print(
                            f"   ⚠️  {py_file.name}:{line_num} - {description}: '{match.group()}'"
                        )
            except Exception:
                continue

    def validate_abaco_data(self):
        """Validate that real Abaco data constants are used."""
        print("\n🔍 Validating real Abaco data usage...")

        schema_file = self.base_path / "config" / "abaco_schema_autodetected.json"

        if schema_file.exists():
            try:
                with open(schema_file) as f:
                    schema = json.load(f)

                abaco_notes = schema.get("notes", {}).get("abaco_integration", {})

                # Validate key metrics
                checks = [
                    (
                        "Portfolio Value",
                        abaco_notes.get("financial_summary", {}).get(
                            "total_loan_exposure_usd"
                        ),
                    ),
                    ("Record Counts", abaco_notes.get("total_records")),
                    (
                        "Currency",
                        (
                            schema.get("datasets", {})
                            .get("Loan Data", {})
                            .get("columns", [{}])[12]
                            .get("sample_values", [None])[0]
                            if len(
                                schema.get("datasets", {})
                                .get("Loan Data", {})
                                .get("columns", [])
                            )
                            > 12
                            else None
                        ),
                    ),
                    (
                        "Apr Range",
                        (
                            schema.get("datasets", {})
                            .get("Loan Data", {})
                            .get("columns", [{}])[13]
                            .get("abaco_validation", {})
                            .get("min_rate")
                            if len(
                                schema.get("datasets", {})
                                .get("Loan Data", {})
                                .get("columns", [])
                            )
                            > 13
                            else None
                        ),
                    ),
                    ("Companies", abaco_notes.get("companies")),
                    (
                        "Product Type",
                        (
                            schema.get("datasets", {})
                            .get("Loan Data", {})
                            .get("columns", [{}])[6]
                            .get("sample_values", [None])[0]
                            if len(
                                schema.get("datasets", {})
                                .get("Loan Data", {})
                                .get("columns", [])
                            )
                            > 6
                            else None
                        ),
                    ),
                ]

                for check_name, value in checks:
                    if value:
                        print(f"   ✅ {check_name}: Found")
                    else:
                        print(f"   ⚠️  {check_name}: Not found")
            except Exception as e:
                self.errors.append(f"Error validating Abaco data: {e}")

    def generate_report(self):
        """Generate validation report."""
        print("\n" + "=" * 70)
        print("📊 REPOSITORY VALIDATION REPORT")
        print("=" * 70)

        # Error summary
        if self.errors:
            print(f"\n❌ Syntax Errors: {len(self.errors)}")
            for error in self.errors[:10]:  # Show first 10
                print(f"   - {error}")
        else:
            print("\n✅ Syntax Errors: 0")

        # Warnings
        print(f"\n✅ Warnings: {len(self.warnings)}")

        # Duplicates
        if self.duplicates:
            print(f"\n⚠️  Duplicate Files: {len(self.duplicates)}")
            for dup_set in self.duplicates[:5]:  # Show first 5
                print(f"   - {len(dup_set)} duplicates of {dup_set[0]}")

        # Dummy data
        if self.dummy_data:
            print(f"\n⚠️  Dummy Data Instances: {len(self.dummy_data)}")
            for item in self.dummy_data[:10]:  # Show first 10
                print(f"   - {item['file']}:{item['line']} - {item['type']}")

        # Real data validation
        print("\n💼 REAL ABACO DATA VALIDATION:")
        print(f"   ✅ Total Records: {self.REAL_DATA['total_records']}")
        print(f"   ✅ Portfolio Value: ${self.REAL_DATA['portfolio_value']:,.2f} USD")
        print(f"   ✅ Companies: {', '.join(self.REAL_DATA['companies'])}")
        print(
            f"   ✅ APR Range: {self.REAL_DATA['apr_range']['min']*100:.2f}% - {self.REAL_DATA['apr_range']['max']*100:.2f}%"
        )
        print(f"   ✅ Product Type: {self.REAL_DATA['product_type']}")

        # Save report
        report_file = self.base_path / "VALIDATION_REPORT.json"
        report_data = {
            "errors": self.errors,
            "warnings": self.warnings,
            "duplicates": [[str(f) for f in dup] for dup in self.duplicates],
            "dummy_data": self.dummy_data,
            "real_data": self.REAL_DATA,
        }

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📋 Report saved to: {report_file}")

        # Final status
        if self.errors:
            print(f"\n⚠️  {len(self.errors)} CRITICAL ISSUES FOUND - NEEDS FIXING")
        else:
            print("\n✅ ALL VALIDATION CHECKS PASSED")

        print("\n" + "=" * 70)
        print("🎯 VALIDATION COMPLETE")
        print("=" * 70)

        return len(self.errors) == 0


if __name__ == "__main__":
    validator = RepositoryValidator()
    success = validator.validate_all()
    exit(0 if success else 1)
