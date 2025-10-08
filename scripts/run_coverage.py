#!/usr/bin/env python3
"""
Enhanced coverage analysis script for Commercial-View commercial lending platform
"""

import subprocess
import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def check_coverage_tools() -> bool:
    """Check if coverage tools are installed"""
    print("🔍 Checking coverage tools...")

    required_tools = ["coverage", "pytest"]
    missing_tools = []

    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print(f"✅ {tool} is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
            print(f"❌ {tool} is not installed")

    if missing_tools:
        print(f"\n💡 Install missing tools: pip install {' '.join(missing_tools)}")
        return False

    return True


def setup_commercial_view_environment() -> None:
    """Setup Commercial-View specific environment for testing"""
    project_root = Path(__file__).parent.parent

    # Set environment variables for testing
    env_vars = {
        "COMMERCIAL_VIEW_ROOT": str(project_root),
        "PYTHONPATH": f"{project_root / 'src'}:{project_root / 'scripts'}",
        "ENVIRONMENT": "testing",
        "DEBUG": "false",
        "PRICING_CONFIG_PATH": str(project_root / "configs" / "pricing_config.yml"),
        "DPD_POLICY_PATH": str(project_root / "configs" / "dpd_policy.yml"),
        "COLUMN_MAPS_PATH": str(project_root / "configs" / "column_maps.yml"),
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    print("🏦 Commercial-View testing environment configured")


def create_coverage_config() -> Path:
    """Create comprehensive coverage configuration for Commercial-View"""
    project_root = Path(__file__).parent.parent
    config_file = project_root / ".coveragerc"

    config_content = """[run]
source = src/
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */venv/*
    */.venv/*
    setup.py
    */migrations/*
    */scripts/debug_*
    */scripts/temp_*

[report]
# Regexes for lines to exclude from consideration
exclude_lines =
    # Have to re-enable the standard pragma
    pragma: no cover
    
    # Don't complain about missing debug-only code:
    def __repr__
    if self\.debug
    
    # Don't complain if tests don't hit defensive assertion code:
    raise AssertionError
    raise NotImplementedError
    
    # Don't complain if non-runnable code isn't run:
    if 0:
    if __name__ == .__main__.:
    
    # Don't complain about abstract methods
    @(abc\.)?abstractmethod

ignore_errors = True
show_missing = True
precision = 2

[html]
directory = htmlcov
title = Commercial-View Coverage Report

[xml]
output = coverage.xml
"""

    with open(config_file, "w") as f:
        f.write(config_content)

    print(f"📄 Created coverage configuration: {config_file}")
    return config_file


def run_commercial_lending_tests() -> Tuple[bool, Dict]:
    """Run Commercial-View commercial lending specific tests"""
    print("\n🏦 Running Commercial Lending Tests...")

    test_categories = {
        "pricing": "tests/test_pricing*.py",
        "dpd": "tests/test_dpd*.py",
        "kpi": "tests/test_kpi*.py",
        "risk": "tests/test_risk*.py",
        "export": "tests/test_export*.py",
        "integration": "tests/integration/",
        "unit": "tests/unit/",
    }

    results = {}

    for category, pattern in test_categories.items():
        print(f"\n📊 Testing {category} components...")

        # Check if test files exist
        test_files = list(Path(".").glob(pattern))
        if not test_files:
            print(f"⚠️  No test files found for {category}")
            results[category] = {"status": "skipped", "reason": "no_tests"}
            continue

        try:
            cmd = ["coverage", "run", "-a", "-m", "pytest", pattern, "-v"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            print(f"✅ {category} tests passed")
            results[category] = {"status": "passed", "output": result.stdout}

        except subprocess.CalledProcessError as e:
            print(f"❌ {category} tests failed")
            results[category] = {"status": "failed", "error": e.stderr}

    return len([r for r in results.values() if r["status"] == "failed"]) == 0, results


def generate_coverage_reports() -> Dict[str, str]:
    """Generate comprehensive coverage reports"""
    print("\n📊 Generating Coverage Reports...")

    reports = {}

    # Console report
    try:
        result = subprocess.run(
            ["coverage", "report", "-m", "--format=text"],
            capture_output=True,
            text=True,
            check=True,
        )
        reports["console"] = result.stdout
        print("✅ Console report generated")
    except subprocess.CalledProcessError as e:
        print(f"❌ Console report failed: {e}")

    # HTML report
    try:
        subprocess.run(["coverage", "html"], check=True, capture_output=True)
        reports["html"] = "htmlcov/index.html"
        print("✅ HTML report generated")
    except subprocess.CalledProcessError as e:
        print(f"❌ HTML report failed: {e}")

    # XML report for CI/CD
    try:
        subprocess.run(["coverage", "xml"], check=True, capture_output=True)
        reports["xml"] = "coverage.xml"
        print("✅ XML report generated")
    except subprocess.CalledProcessError as e:
        print(f"❌ XML report failed: {e}")

    # JSON report for programmatic access
    try:
        subprocess.run(["coverage", "json"], check=True, capture_output=True)
        reports["json"] = "coverage.json"
        print("✅ JSON report generated")
    except subprocess.CalledProcessError as e:
        print(f"❌ JSON report failed: {e}")

    return reports


def analyze_coverage_results() -> Dict:
    """Analyze coverage results and provide insights"""
    coverage_json = Path("coverage.json")

    if not coverage_json.exists():
        return {"error": "Coverage JSON not found"}

    try:
        with open(coverage_json, "r") as f:
            coverage_data = json.load(f)

        total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

        # Analyze by Commercial-View modules
        module_coverage = {}
        for filename, file_data in coverage_data.get("files", {}).items():
            if "commercial_view" in filename:
                module_name = filename.split("/")[-2] if "/" in filename else "core"
                if module_name not in module_coverage:
                    module_coverage[module_name] = []
                module_coverage[module_name].append(
                    {
                        "file": filename,
                        "coverage": file_data.get("summary", {}).get(
                            "percent_covered", 0
                        ),
                    }
                )

        # Calculate module averages
        module_averages = {}
        for module, files in module_coverage.items():
            avg_coverage = sum(f["coverage"] for f in files) / len(files)
            module_averages[module] = {
                "average": round(avg_coverage, 2),
                "file_count": len(files),
                "files": files,
            }

        return {
            "total_coverage": total_coverage,
            "module_coverage": module_averages,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"error": f"Failed to analyze coverage: {e}"}


def create_coverage_summary_report(analysis: Dict, reports: Dict) -> None:
    """Create a comprehensive coverage summary report"""
    report_dir = Path("coverage_reports")
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = report_dir / f"coverage_summary_{timestamp}.md"

    with open(summary_file, "w") as f:
        f.write("# Commercial-View Coverage Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        if "error" in analysis:
            f.write(f"## Error\n\n{analysis['error']}\n\n")
            return

        # Overall coverage
        total_coverage = analysis.get("total_coverage", 0)
        f.write(f"## Overall Coverage: {total_coverage:.1f}%\n\n")

        # Coverage status badge
        if total_coverage >= 90:
            badge = "🟢 Excellent"
        elif total_coverage >= 80:
            badge = "🟡 Good"
        elif total_coverage >= 70:
            badge = "🟠 Fair"
        else:
            badge = "🔴 Needs Improvement"

        f.write(f"**Status:** {badge}\n\n")

        # Module coverage breakdown
        f.write("## Module Coverage Breakdown\n\n")
        f.write("| Module | Coverage | Files | Status |\n")
        f.write("|--------|----------|-------|--------|\n")

        for module, data in analysis.get("module_coverage", {}).items():
            coverage = data["average"]
            file_count = data["file_count"]
            status = "✅" if coverage >= 80 else "⚠️" if coverage >= 60 else "❌"
            f.write(f"| {module} | {coverage:.1f}% | {file_count} | {status} |\n")

        # Recommendations
        f.write("\n## Recommendations\n\n")

        low_coverage_modules = [
            module
            for module, data in analysis.get("module_coverage", {}).items()
            if data["average"] < 70
        ]

        if low_coverage_modules:
            f.write("### Modules Needing Attention\n\n")
            for module in low_coverage_modules:
                f.write(f"- **{module}**: Add more comprehensive tests\n")

        if total_coverage < 80:
            f.write("\n### General Recommendations\n\n")
            f.write("- Focus on testing core commercial lending functions\n")
            f.write("- Add integration tests for pricing models\n")
            f.write("- Include edge case testing for DPD calculations\n")
            f.write("- Test error handling and validation\n")

        # Report locations
        f.write("\n## Generated Reports\n\n")
        for report_type, location in reports.items():
            f.write(f"- **{report_type.upper()}**: `{location}`\n")

    print(f"📋 Coverage summary report: {summary_file}")


def run_coverage_analysis():
    """Run comprehensive coverage analysis for Commercial-View"""
    print("🏦 Running Commercial-View Coverage Analysis")
    print("=" * 60)

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check tools
    if not check_coverage_tools():
        return False

    # Setup environment
    setup_commercial_view_environment()

    # Create coverage configuration
    create_coverage_config()

    # Clear previous coverage data
    coverage_files = [".coverage", "coverage.xml", "coverage.json"]
    for file in coverage_files:
        if Path(file).exists():
            Path(file).unlink()

    if Path("htmlcov").exists():
        shutil.rmtree("htmlcov")

    print("🧹 Cleared previous coverage data")

    # Run tests with coverage
    success, test_results = run_commercial_lending_tests()

    if not success:
        print("\n❌ Some tests failed - coverage may be incomplete")
        print("💡 Fix failing tests and re-run coverage analysis")

    # Generate reports
    reports = generate_coverage_reports()

    # Analyze results
    analysis = analyze_coverage_results()

    # Create summary report
    create_coverage_summary_report(analysis, reports)

    # Display results
    print(f"\n📊 Coverage Analysis Results:")
    if "total_coverage" in analysis:
        print(f"   Total Coverage: {analysis['total_coverage']:.1f}%")

        print(f"\n🏦 Commercial Lending Module Coverage:")
        for module, data in analysis.get("module_coverage", {}).items():
            status = (
                "✅"
                if data["average"] >= 80
                else "⚠️" if data["average"] >= 60 else "❌"
            )
            print(
                f"   {status} {module}: {data['average']:.1f}% ({data['file_count']} files)"
            )

    print(f"\n📁 Generated Reports:")
    for report_type, location in reports.items():
        print(f"   {report_type.upper()}: {location}")

    if "html" in reports:
        print(f"\n💡 View detailed HTML report: open {reports['html']}")

    return success


if __name__ == "__main__":
    success = run_coverage_analysis()
    sys.exit(0 if success else 1)
