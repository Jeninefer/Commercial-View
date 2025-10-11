"""
Test script for the Commercial-View Schema Parser

Usage:
    cd /Users/jenineferderas/Documents/GitHub/Commercial-View
    python test_schema_parser.py
"""

import sys
from pathlib import Path

# Ensure we're running from project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.schema_parser import (
    load_schema,
    list_datasets,
    get_dataset_info,
    categorize_field,
    get_schema_summary,
    validate_dataset_schema,
    export_schema_documentation,
)


def main():
    """Run comprehensive tests on the schema parser"""
    print("=" * 70)
    print("Commercial-View Schema Parser Test Suite")
    print("=" * 70)
    
    # Path to your schema file
    schema_path = project_root / "Downloads" / "abaco_schema_autodetected.json"
    
    if not schema_path.exists():
        print(f"\n❌ Schema file not found: {schema_path}")
        print("\nSearching for schema file...")
        
        # Try alternative locations
        alt_paths = [
            project_root / "data" / "abaco_schema_autodetected.json",
            project_root / "abaco_schema_autodetected.json",
        ]
        
        for alt_path in alt_paths:
            if alt_path.exists():
                schema_path = alt_path
                print(f"✅ Found schema at: {schema_path}")
                break
        else:
            print("\nPlease place the schema file at one of these locations:")
            print(f"  1. {project_root / 'Downloads' / 'abaco_schema_autodetected.json'}")
            print(f"  2. {project_root / 'data' / 'abaco_schema_autodetected.json'}")
            return 1
    
    try:
        # Test 1: Load Schema
        print("\n📁 Test 1: Loading Schema")
        print("-" * 70)
        schema = load_schema(schema_path)
        print("✅ Schema loaded successfully")
        
        # Test 2: List Datasets
        print("\n📊 Test 2: Listing Datasets")
        print("-" * 70)
        datasets = list_datasets(schema)
        print(f"✅ Found {len(datasets)} datasets:")
        for dataset in datasets:
            print(f"   - {dataset}")
        
        # Test 3: Analyze First Dataset
        if datasets:
            print(f"\n🔍 Test 3: Analyzing '{datasets[0]}'")
            print("-" * 70)
            dataset_info = get_dataset_info(schema, datasets[0])
            print(f"   Columns: {len(dataset_info.columns)}")
            print(f"   First 3 columns:")
            for col in dataset_info.columns[:3]:
                category = categorize_field(col.name)
                print(f"      - {col.name} ({col.dtype}) [{category}]")
        
        # Test 4: Generate Summary
        print("\n📈 Test 4: Generating Summary")
        print("-" * 70)
        summary = get_schema_summary(schema)
        print(f"✅ Total Datasets: {summary['total_datasets']}")
        print(f"   Total Columns: {summary['total_columns']}")
        
        # Test 5: Export Documentation
        print("\n📄 Test 5: Exporting Documentation")
        print("-" * 70)
        doc_path = project_root / "docs" / "schema_documentation.md"
        doc_path.parent.mkdir(exist_ok=True)
        export_schema_documentation(schema, doc_path)
        print(f"✅ Documentation exported to: {doc_path}")
        
        print("\n" + "=" * 70)
        print("✅ All Tests Completed Successfully!")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
        print("\n   Business Categories:")
        for category, count in sorted(summary['business_categories'].items(), 
                                      key=lambda x: x[1], reverse=True)[:5]:
            print(f"      - {category}: {count}")
        
        # Test 6: Export Documentation
        print("\n📄 Test 6: Exporting Documentation")
        print("-" * 70)
        doc_path = Path(__file__).parent / "docs" / "schema_documentation.md"
        doc_path.parent.mkdir(exist_ok=True)
        
        export_schema_documentation(schema, doc_path)
        print(f"✅ Documentation exported to:")
        print(f"   {doc_path}")
        
        # Test 7: Test Specific Field Categorization
        print("\n🏷️  Test 7: Field Categorization Examples")
        print("-" * 70)
        test_fields = [
            "Loan ID",
            "Disbursement Amount",
            "Interest Rate APR",
            "Payment Date",
            "Loan Status",
            "Days in Default",
            "Customer ID",
            "True Total Payment"
        ]
        
        for field in test_fields:
            category = categorize_field(field)
            print(f"   {field:30s} → {category}")
        
        print("\n" + "=" * 70)
        print("✅ All Tests Completed Successfully!")
        print("=" * 70)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
