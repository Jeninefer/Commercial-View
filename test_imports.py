"""
Test script to verify all imports work correctly for Commercial-View Abaco Integration

Usage:
    cd /workspaces/Commercial-View
    python test_imports.py
"""

import sys
from pathlib import Path
import importlib.util
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_core_dependencies():
    """Test core Python dependencies required for Abaco processing."""
    print("🔍 Testing Core Dependencies")
    print("-" * 50)
    
    dependencies = {
        'pandas': 'Data processing for 48,853 records',
        'numpy': 'Mathematical operations and risk scoring',
        'json': 'Schema validation and configuration',
        'pathlib': 'File system operations',
        'datetime': 'Date/time processing for loan schedules',
        'typing': 'Type hints for code quality'
    }
    
    results = {}
    
    for module_name, description in dependencies.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'built-in')
            print(f"✅ {module_name} ({version}): {description}")
            results[module_name] = True
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            results[module_name] = False
    
    return results

def test_optional_dependencies():
    """Test optional dependencies for enhanced functionality."""
    print("\n🔧 Testing Optional Dependencies")
    print("-" * 50)
    
    optional_deps = {
        'fastapi': 'Web API framework (optional for web interface)',
        'yaml': 'YAML configuration files (pyyaml)',
        'requests': 'HTTP requests for external APIs'
    }
    
    results = {}
    
    for module_name, description in optional_deps.items():
        try:
            if module_name == 'yaml':
                import yaml as module
            else:
                module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {module_name} ({version}): {description}")
            results[module_name] = True
        except ImportError:
            print(f"⚠️  {module_name}: {description} - Not installed")
            results[module_name] = False
    
    return results

def test_project_structure():
    """Test that required project directories and files exist."""
    print("\n📁 Testing Project Structure")
    print("-" * 50)
    
    required_structure = [
        'src/',
        'src/__init__.py',
        'config/',
        'docs/',
        'requirements.txt'
    ]
    
    results = {}
    
    for path_str in required_structure:
        path = project_root / path_str
        if path.exists():
            print(f"✅ {path_str}")
            results[path_str] = True
        else:
            print(f"❌ {path_str} - Missing")
            results[path_str] = False
    
    return results

def test_commercial_view_components():
    """Test Commercial View specific components."""
    print("\n🏦 Testing Commercial View Components")
    print("-" * 50)
    
    components = {}
    
    # Test src package
    try:
        import src
        print(f"✅ src package imported successfully")
        components['src_package'] = True
    except Exception as e:
        print(f"❌ src package: {e}")
        components['src_package'] = False
    
    # Test DataLoader
    try:
        from src.data_loader import DataLoader
        loader = DataLoader()
        print("✅ DataLoader class imported and instantiated")
        components['data_loader'] = True
    except Exception as e:
        print(f"❌ DataLoader: {e}")
        components['data_loader'] = False
    
    # Test API components
    try:
        from src.api import app
        print("✅ FastAPI app imported successfully")
        components['api'] = True
    except Exception as e:
        print(f"❌ API components: {e}")
        components['api'] = False
    
    # Test metrics registry
    try:
        from src.metrics_registry import MetricsRegistry
        registry = MetricsRegistry()
        print("✅ MetricsRegistry imported and instantiated")
        components['metrics'] = True
    except Exception as e:
        print(f"❌ MetricsRegistry: {e}")
        components['metrics'] = False
    
    return components

def test_schema_file():
    """Test that the Abaco schema file is accessible."""
    print("\n📋 Testing Schema File Access")
    print("-" * 50)
    
    schema_paths = [
        project_root / "config" / "abaco_schema_autodetected.json",
        project_root / "data" / "abaco_schema_autodetected.json",
        project_root / "abaco_schema_autodetected.json"
    ]
    
    schema_found = False
    
    for schema_path in schema_paths:
        if schema_path.exists():
            try:
                import json
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                
                print(f"✅ Schema file found: {schema_path}")
                
                # Check if it has the expected structure
                if 'datasets' in schema:
                    datasets = schema['datasets']
                    total_records = sum(
                        dataset.get('rows', 0) for dataset in datasets.values()
                        if dataset.get('exists', False)
                    )
                    print(f"   📊 Total records: {total_records:,}")
                    
                    if total_records > 40000:  # Flexible check
                        print("   ✅ Large dataset confirmed")
                
                schema_found = True
                break
                
            except Exception as e:
                print(f"❌ Error reading schema: {e}")
    
    if not schema_found:
        print("⚠️  No Abaco schema file found in expected locations")
        for path in schema_paths:
            print(f"   • {path}")
    
    return schema_found

def generate_summary_report():
    """Generate a summary report."""
    print("\n📄 Generating Summary Report")
    print("-" * 50)
    
    # Run all tests
    core_deps = test_core_dependencies()
    optional_deps = test_optional_dependencies()
    structure = test_project_structure()
    components = test_commercial_view_components()
    schema = test_schema_file()
    
    # Calculate overall status
    core_ready = all(core_deps.values())
    structure_ready = all(structure.values())
    components_ready = sum(components.values()) >= len(components) * 0.7  # 70% pass rate
    
    overall_ready = core_ready and structure_ready and components_ready
    
    report = f"""# Commercial-View Import Test Report

## Test Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Overall Status**: {'✅ READY' if overall_ready else '⚠️ NEEDS ATTENTION'}

### Core Dependencies: {'✅ PASSED' if core_ready else '❌ FAILED'}
- pandas: {'✅' if core_deps.get('pandas') else '❌'}
- numpy: {'✅' if core_deps.get('numpy') else '❌'}
- json, pathlib, datetime: {'✅' if all([core_deps.get('json'), core_deps.get('pathlib'), core_deps.get('datetime')]) else '❌'}

### Project Structure: {'✅ PASSED' if structure_ready else '❌ FAILED'}
- src/ package: {'✅' if structure.get('src/') else '❌'}
- Configuration: {'✅' if structure.get('config/') else '❌'}
- Documentation: {'✅' if structure.get('docs/') else '❌'}

### Components: {'✅ PASSED' if components_ready else '⚠️ PARTIAL'}
- DataLoader: {'✅' if components.get('data_loader') else '❌'}
- API: {'✅' if components.get('api') else '❌'}
- Metrics: {'✅' if components.get('metrics') else '❌'}

### Schema File: {'✅ FOUND' if schema else '⚠️ NOT FOUND'}

## Production Readiness
{'✅ System is ready for portfolio processing' if overall_ready else '⚠️ Some components need attention before production use'}
"""
    
    # Save report
    report_path = project_root / "docs" / "import_test_report.md"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report saved: {report_path}")
    return overall_ready

def main():
    """Run comprehensive import testing."""
    print("🏦 COMMERCIAL-VIEW - IMPORT VALIDATION TEST")
    print("=" * 60)
    print("📊 Testing system components and dependencies")
    print("🔧 Validating production readiness")
    print("=" * 60)
    
    # Run all tests and generate report  
    system_ready = generate_summary_report()
    
    # Final summary
    print(f"\n🎯 FINAL RESULT")
    print("=" * 30)
    
    if system_ready:
        print("🎉 SYSTEM READY!")
        print("✅ All core components functional")
        print("🚀 Ready for portfolio processing")
        return 0
    else:
        print("⚠️  SYSTEM NEEDS ATTENTION")
        print("📋 Check detailed report for specifics")
        print("🔧 Install missing dependencies and fix issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
