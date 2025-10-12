"""
Final repository audit for Commercial-View
Ensures 100% English content with zero demo/example data
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple


class FinalRepositoryAuditor:
    """Comprehensive audit for production-ready Commercial-View repository"""

    def __init__(self):
        self.repo_root = Path("/Users/jenineferderas/Commercial-View")
        self.issues = []
        self.validated_files = []

    def audit_complete_repository(self) -> Dict[str, any]:
        """Perform comprehensive repository audit"""

        audit_results = {
            "language_compliance": self._audit_language_compliance(),
            "demo_data_check": self._audit_demo_data(),
            "production_readiness": self._audit_production_readiness(),
            "documentation_quality": self._audit_documentation(),
            "code_quality": self._audit_code_quality(),
            "summary": {},
        }

        audit_results["summary"] = self._generate_audit_summary(audit_results)
        return audit_results

    def _audit_language_compliance(self) -> Dict[str, any]:
        """Ensure 100% English language compliance"""

        non_english_patterns = [
            r"[^\x00-\x7F]+",  # Non-ASCII characters
            r"\b(español|français|deutsch|italiano|português)\b",  # Common languages
            r"[\u00C0-\u017F]+",  # Latin extended characters
            r"[\u0100-\u024F]+",  # Latin extended additional
        ]

        issues = []
        english_files = 0

        for file_path in self._get_text_files():
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern in non_english_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        issues.append(
                            {
                                "file": str(file_path.relative_to(self.repo_root)),
                                "issue": "Non-English content detected",
                                "matches": matches[:5],  # First 5 matches
                            }
                        )

                english_files += 1

            except Exception as e:
                issues.append(
                    {
                        "file": str(file_path.relative_to(self.repo_root)),
                        "issue": f"File read error: {e}",
                    }
                )

        return {
            "compliant": len(issues) == 0,
            "files_checked": english_files,
            "issues": issues,
            "status": (
                "✅ 100% English"
                if len(issues) == 0
                else f"❌ {len(issues)} issues found"
            ),
        }

    def _audit_demo_data(self) -> Dict[str, any]:
        """Ensure zero demo/example data"""

        demo_indicators = [
            # File naming patterns
            r".*demo.*\.csv$",
            r".*example.*\.csv$",
            r".*sample.*\.csv$",
            r".*test.*\.csv$",
            r".*mock.*\.csv$",
            # Content patterns
            r"\b(demo|example|sample|mock|fake|test).*data\b",
            r"\b(lorem ipsum|placeholder|dummy)\b",
            r"\bJohn Doe\b|\bJane Smith\b|\bAcme Corp\b",
            r"\b(555-)\d{4}\b",  # Fake phone numbers
            r"\bexample\.com\b|\btest\.com\b",
            # Code patterns
            r"generate.*sample.*data",
            r"create.*demo.*",
            r"mock.*generator",
            r"faker\.",
        ]

        demo_files = []
        content_issues = []

        # Check file names
        for file_path in self.repo_root.rglob("*"):
            if file_path.is_file():
                filename = file_path.name.lower()
                for pattern in demo_indicators[:5]:  # File naming patterns
                    if re.match(pattern, filename):
                        demo_files.append(str(file_path.relative_to(self.repo_root)))

        # Check file contents
        for file_path in self._get_text_files():
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()

                for pattern in demo_indicators[5:]:  # Content patterns
                    if re.search(pattern, content, re.IGNORECASE):
                        content_issues.append(
                            {
                                "file": str(file_path.relative_to(self.repo_root)),
                                "pattern": pattern,
                                "context": self._extract_context(content, pattern),
                            }
                        )

            except Exception:
                continue

        return {
            "demo_free": len(demo_files) == 0 and len(content_issues) == 0,
            "demo_files": demo_files,
            "content_issues": content_issues,
            "status": (
                "✅ Zero demo data"
                if len(demo_files) == 0 and len(content_issues) == 0
                else f"❌ {len(demo_files + content_issues)} demo references found"
            ),
        }

    def _audit_production_readiness(self) -> Dict[str, any]:
        """Audit production readiness indicators"""

        production_requirements = {
            "environment_configs": [".env.example", "configs/production.yml"],
            "security_files": [".gitignore", "requirements.txt"],
            "documentation": ["README.md", "docs/"],
            "testing": ["tests/", "pytest.ini"],
            "ci_cd": [".github/workflows/"],
            "data_sources": ["data/", "scripts/refresh_production_data.py"],
        }

        compliance = {}

        for category, required_paths in production_requirements.items():
            category_compliance = []

            for req_path in required_paths:
                full_path = self.repo_root / req_path
                exists = full_path.exists()
                category_compliance.append(
                    {
                        "path": req_path,
                        "exists": exists,
                        "type": "directory" if full_path.is_dir() else "file",
                    }
                )

            compliance[category] = {
                "items": category_compliance,
                "compliant": all(item["exists"] for item in category_compliance),
            }

        overall_compliant = all(cat["compliant"] for cat in compliance.values())

        return {
            "production_ready": overall_compliant,
            "categories": compliance,
            "status": (
                "✅ Production ready"
                if overall_compliant
                else "❌ Missing production requirements"
            ),
        }

    def _audit_documentation(self) -> Dict[str, any]:
        """Audit documentation completeness and quality"""

        required_docs = [
            "README.md",
            "docs/index.md",
            "docs/quickstart.md",
            "docs/architecture-overview.md",
            "docs/implementation-guide.md",
            "docs/testing-and-quality.md",
            "docs/ai-integrations.md",
            "docs/api-reference.md",
            "docs/secrets-management.md",
        ]

        doc_analysis = {}
        total_words = 0

        for doc_path in required_docs:
            full_path = self.repo_root / doc_path

            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    word_count = len(content.split())
                    total_words += word_count

                    doc_analysis[doc_path] = {
                        "exists": True,
                        "word_count": word_count,
                        "has_toc": "## " in content or "### " in content,
                        "has_examples": "```" in content,
                    }

                except Exception as e:
                    doc_analysis[doc_path] = {"exists": True, "error": str(e)}
            else:
                doc_analysis[doc_path] = {"exists": False}

        return {
            "complete_documentation": all(
                doc.get("exists", False) for doc in doc_analysis.values()
            ),
            "total_word_count": total_words,
            "meets_word_target": total_words >= 40000,
            "documents": doc_analysis,
            "status": (
                f"✅ {total_words:,} words"
                if total_words >= 40000
                else f"❌ {total_words:,} words (target: 40,000+)"
            ),
        }

    def _audit_code_quality(self) -> Dict[str, any]:
        """Audit code quality and completeness"""

        code_requirements = {
            "typescript_files": list(self.repo_root.rglob("*.ts"))
            + list(self.repo_root.rglob("*.tsx")),
            "python_files": list(self.repo_root.rglob("*.py")),
            "test_files": list(self.repo_root.glob("tests/test_*.py"))
            + list(self.repo_root.rglob("*.test.ts*")),
            "config_files": list(self.repo_root.rglob("*.yml"))
            + list(self.repo_root.rglob("*.yaml"))
            + list(self.repo_root.rglob("*.json")),
        }

        quality_metrics = {}

        for category, files in code_requirements.items():
            quality_metrics[category] = {
                "file_count": len(files),
                "total_lines": sum(self._count_lines(f) for f in files if f.is_file()),
                "files": [
                    str(f.relative_to(self.repo_root)) for f in files[:5]
                ],  # First 5 files
            }

        return {
            "high_quality_code": quality_metrics["typescript_files"]["file_count"] > 0
            and quality_metrics["python_files"]["file_count"] > 0,
            "comprehensive_tests": quality_metrics["test_files"]["file_count"] >= 31,
            "metrics": quality_metrics,
            "status": (
                "✅ High quality codebase"
                if quality_metrics["test_files"]["file_count"] >= 31
                else f"❌ {quality_metrics['test_files']['file_count']} test files (target: 31+)"
            ),
        }

    def _get_text_files(self) -> List[Path]:
        """Get all text files for content analysis"""
        text_extensions = {
            ".md",
            ".py",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".yml",
            ".yaml",
            ".json",
            ".txt",
            ".csv",
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

    def _extract_context(
        self, content: str, pattern: str, context_length: int = 100
    ) -> str:
        """Extract context around pattern match"""
        try:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                start = max(0, match.start() - context_length // 2)
                end = min(len(content), match.end() + context_length // 2)
                return f"...{content[start:end]}..."
        except Exception as e:
            pass
        return ""

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except Exception as e:
            return 0

    def _generate_audit_summary(self, audit_results: Dict) -> Dict[str, any]:
        """Generate comprehensive audit summary"""

        all_checks = [
            audit_results["language_compliance"]["compliant"],
            audit_results["demo_data_check"]["demo_free"],
            audit_results["production_readiness"]["production_ready"],
            audit_results["documentation_quality"]["complete_documentation"],
            audit_results["code_quality"]["high_quality_code"],
        ]

        overall_score = sum(all_checks) / len(all_checks) * 100

        return {
            "overall_compliant": all(all_checks),
            "compliance_score": f"{overall_score:.1f}%",
            "checks_passed": sum(all_checks),
            "total_checks": len(all_checks),
            "status": "✅ PRODUCTION READY" if all(all_checks) else "❌ ISSUES FOUND",
            "final_assessment": (
                "Enterprise-grade Commercial-View implementation"
                if all(all_checks)
                else "Requires remediation before production"
            ),
        }


def run_final_audit():
    """Execute final repository audit"""
    print("🔍 FINAL COMMERCIAL-VIEW REPOSITORY AUDIT")
    print("=" * 60)
    print("Validating: 100% English content, zero demo data, production readiness")
    print()

    auditor = FinalRepositoryAuditor()
    results = auditor.audit_complete_repository()

    # Print results
    for category, data in results.items():
        if category != "summary":
            print(
                f"{category.replace('_', ' ').title()}: {data.get('status', 'Unknown')}"
            )

    print()
    print("FINAL ASSESSMENT")
    print("-" * 30)
    summary = results["summary"]
    print(f"Overall Status: {summary['status']}")
    print(f"Compliance Score: {summary['compliance_score']}")
    print(f"Checks Passed: {summary['checks_passed']}/{summary['total_checks']}")
    print(f"Assessment: {summary['final_assessment']}")

    return results


if __name__ == "__main__":
    audit_results = run_final_audit()

    # Exit with appropriate code
    if audit_results["summary"]["overall_compliant"]:
        print("\n🎉 Repository passes all production requirements!")
        exit(0)
    else:
        print("\n💥 Repository requires fixes before production deployment")
        exit(1)
