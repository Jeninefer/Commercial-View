"""
Final production validation for Commercial-View
Comprehensive check for English-only content and zero demo data
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime


class CommercialViewProductionValidator:
    """Comprehensive production validator for Commercial-View repository"""

    def __init__(self):
        self.repo_root = Path.cwd()
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "english_compliance": {"status": False, "issues": []},
            "demo_data_check": {"status": False, "issues": []},
            "production_readiness": {"status": False, "issues": []},
            "file_analysis": {"total_files": 0, "validated_files": 0},
            "overall_status": "FAILED",
        }

    def run_complete_validation(self) -> Dict:
        """Run comprehensive production validation"""

        print("🔍 COMMERCIAL-VIEW PRODUCTION VALIDATION")
        print("=" * 60)
        print("Ensuring 100% English content with zero demo data")
        print()

        # Step 1: Validate English-only content
        self._validate_english_compliance()

        # Step 2: Check for demo/example data
        self._validate_no_demo_data()

        # Step 3: Verify production readiness
        self._validate_production_readiness()

        # Step 4: Generate final assessment
        self._generate_final_assessment()

        return self.validation_results

    def _validate_english_compliance(self):
        """Validate all content is professional English"""
        print("📝 Validating English-only content...")

        issues = []
        validated_files = 0

        # Patterns for non-English content
        non_english_patterns = [
            (r"[^\x00-\x7F]+", "Non-ASCII characters detected"),
            (
                r"\b(español|français|deutsch|italiano|português|中文|日本語)\b",
                "Non-English language detected",
            ),
            (r"[\u0100-\u017F]+", "Extended Latin characters detected"),
            (r"[\u0180-\u024F]+", "Latin extended-B characters detected"),
        ]

        # Check text files
        for file_path in self._get_text_files():
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern, description in non_english_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        issues.append(
                            {
                                "file": str(file_path.relative_to(self.repo_root)),
                                "issue": description,
                                "matches": matches[:3],  # Show first 3 matches
                            }
                        )

                validated_files += 1

            except Exception as e:
                issues.append(
                    {
                        "file": str(file_path.relative_to(self.repo_root)),
                        "issue": f"File read error: {e}",
                    }
                )

        self.validation_results["english_compliance"] = {
            "status": len(issues) == 0,
            "issues": issues,
            "files_validated": validated_files,
        }

        if len(issues) == 0:
            print(f"✅ English compliance: {validated_files} files validated")
        else:
            print(f"❌ English compliance: {len(issues)} issues found")

    def _validate_no_demo_data(self):
        """Validate zero demo or example data exists"""
        print("🧹 Checking for demo/example data...")

        demo_indicators = [
            # Content patterns
            (r"\b(demo|example|sample|mock|fake|test).*data\b", "Demo data reference"),
            (r"\b(lorem ipsum|placeholder|dummy)\b", "Placeholder content"),
            (r"\bJohn Doe\b|\bJane Smith\b|\bAcme Corp\b", "Demo names"),
            (r"\b(555-)\d{4}\b", "Fake phone numbers"),
            (r"\bexample\.com\b|\btest\.com\b|\bdemo\.com\b", "Demo domains"),
            # Code patterns
            (r"generate.*sample.*data", "Sample data generator"),
            (r"create.*demo.*", "Demo creator"),
            (r"mock.*generator", "Mock data generator"),
        ]

        issues = []

        # Check file names for demo indicators
        for file_path in self.repo_root.rglob("*"):
            if file_path.is_file():
                filename = file_path.name.lower()
                if any(
                    term in filename
                    for term in ["demo", "example", "sample", "mock", "test_"]
                ):
                    # Exclude legitimate test files in tests directory
                    if "tests/" not in str(file_path) and "test_" in filename:
                        issues.append(
                            {
                                "file": str(file_path.relative_to(self.repo_root)),
                                "issue": "Demo/test file outside tests directory",
                            }
                        )

        # Check file contents
        for file_path in self._get_text_files():
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()

                for pattern, description in demo_indicators:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(
                            {
                                "file": str(file_path.relative_to(self.repo_root)),
                                "issue": description,
                                "pattern": pattern,
                            }
                        )

            except Exception:
                continue

        self.validation_results["demo_data_check"] = {
            "status": len(issues) == 0,
            "issues": issues,
        }

        if len(issues) == 0:
            print("✅ Demo data check: Zero demo content found")
        else:
            print(f"❌ Demo data check: {len(issues)} issues found")

    def _validate_production_readiness(self):
        """Validate production readiness indicators"""
        print("🚀 Validating production readiness...")

        production_requirements = {
            "source_code": {"src/", "frontend/"},
            "documentation": {"README.md", "docs/"},
            "configuration": {".env.example", "requirements.txt"},
            "real_data_source": {"data/", "scripts/upload_to_drive.py"},
            "validation_scripts": {"scripts/"},
        }

        issues = []

        for category, required_items in production_requirements.items():
            missing_items = []

            for item in required_items:
                item_path = self.repo_root / item
                if not item_path.exists():
                    missing_items.append(item)

            if missing_items:
                issues.append({"category": category, "missing": missing_items})

        # Check for real data connection
        google_drive_url = (
            "https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
        )
        has_real_data_connection = False

        for file_path in self._get_text_files():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if google_drive_url in content:
                        has_real_data_connection = True
                        break
            except:
                continue

        if not has_real_data_connection:
            issues.append(
                {
                    "category": "data_connection",
                    "missing": ["Real Google Drive data source not found"],
                }
            )

        self.validation_results["production_readiness"] = {
            "status": len(issues) == 0,
            "issues": issues,
            "real_data_connected": has_real_data_connection,
        }

        if len(issues) == 0:
            print("✅ Production readiness: All requirements met")
        else:
            print(f"❌ Production readiness: {len(issues)} issues found")

    def _get_text_files(self) -> List[Path]:
        """Get all text files for analysis"""
        text_extensions = {
            ".py",
            ".md",
            ".txt",
            ".json",
            ".yml",
            ".yaml",
            ".csv",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
        }
        exclude_patterns = {
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            ".pytest_cache",
        }

        text_files = []

        for file_path in self.repo_root.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in text_extensions
                and not any(exc in str(file_path) for exc in exclude_patterns)
            ):
                text_files.append(file_path)

        return text_files

    def _generate_final_assessment(self):
        """Generate final production assessment"""
        print("\n📊 FINAL PRODUCTION ASSESSMENT")
        print("-" * 40)

        checks = [
            self.validation_results["english_compliance"]["status"],
            self.validation_results["demo_data_check"]["status"],
            self.validation_results["production_readiness"]["status"],
        ]

        all_passed = all(checks)
        passed_count = sum(checks)

        self.validation_results["overall_status"] = (
            "PRODUCTION_READY" if all_passed else "NEEDS_FIXES"
        )

        print(f"English Compliance: {'✅' if checks[0] else '❌'}")
        print(f"Demo Data Check: {'✅' if checks[1] else '❌'}")
        print(f"Production Ready: {'✅' if checks[2] else '❌'}")
        print()
        print(
            f"Overall Status: {'🎉 PRODUCTION READY' if all_passed else '⚠️ NEEDS FIXES'}"
        )
        print(f"Checks Passed: {passed_count}/3")

        if all_passed:
            print("\n🏆 COMMERCIAL-VIEW CERTIFICATION")
            print("✅ 100% English professional content")
            print("✅ Zero demo or example data")
            print("✅ Real commercial lending data sources")
            print("✅ Production-ready for commercial deployment")
            print("\nRepository is certified for commercial lending production use.")
        else:
            print("\n💥 ISSUES REQUIRING ATTENTION")
            for category, data in self.validation_results.items():
                if (
                    isinstance(data, dict)
                    and not data.get("status", True)
                    and "issues" in data
                ):
                    print(f"\n{category.replace('_', ' ').title()}:")
                    for issue in data["issues"][:3]:  # Show first 3 issues
                        if isinstance(issue, dict):
                            print(
                                f"  - {issue.get('file', 'Unknown')}: {issue.get('issue', 'Unknown issue')}"
                            )

    def save_validation_report(self):
        """Save validation report to file"""
        report_file = self.repo_root / "PRODUCTION_VALIDATION_REPORT.json"

        with open(report_file, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        print(f"\n📋 Validation report saved: {report_file}")


def main():
    """Main execution function"""
    validator = CommercialViewProductionValidator()
    results = validator.run_complete_validation()
    validator.save_validation_report()

    # Exit with appropriate code
    if results["overall_status"] == "PRODUCTION_READY":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
