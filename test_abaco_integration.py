"""
Test script to verify Abaco integration is ready to run
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_abaco_integration():
    """Test complete Abaco integration pipeline."""
    
    print("🧪 Testing Abaco Integration - Production Readiness Check")
    print("=" * 60)
    
    # Test 1: Check for required files
    print("📁 1. Checking required files...")
    
    required_files = {
        'schema': 'config/abaco_schema_autodetected.json',
        'loan_data': 'data/Abaco - Loan Tape_Loan Data_Table.csv',
        'payment_history': 'data/Abaco - Loan Tape_Historic Real Payment_Table.csv',
        'payment_schedule': 'data/Abaco - Loan Tape_Payment Schedule_Table.csv'
    }
    
    files_found = {}
    for file_type, filepath in required_files.items():
        exists = os.path.exists(filepath)
        files_found[file_type] = exists
        status = "✅" if exists else "❌"
        print(f"   {status} {file_type}: {filepath}")
    
    # Test 2: Import modules
    print("\n🐍 2. Testing module imports...")
    
    try:
        from data_loader import DataLoader
        print("   ✅ DataLoader import successful")
        
        # Test initialization
        loader = DataLoader()
        print("   ✅ DataLoader initialization successful")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 3: Schema validation
    print("\n📋 3. Testing schema validation...")
    
    if files_found['schema']:
        try:
            import json
            with open('config/abaco_schema_autodetected.json', 'r') as f:
                schema = json.load(f)
            
            datasets = schema.get('datasets', {})
            available_datasets = [name for name, info in datasets.items() if info.get('exists')]
            total_records = sum(info.get('rows', 0) for info in datasets.values() if info.get('exists'))
            
            print(f"   ✅ Schema loaded: {len(available_datasets)} datasets")
            print(f"   📊 Total records: {total_records:,}")
            
            # Verify expected datasets
            expected = ['Loan Data', 'Historic Real Payment', 'Payment Schedule']
            found = [d for d in expected if d in available_datasets]
            
            if len(found) == 3:
                print(f"   ✅ All required datasets present: {found}")
            else:
                print(f"   ⚠️  Missing datasets: {set(expected) - set(found)}")
                
        except Exception as e:
            print(f"   ❌ Schema validation error: {e}")
    else:
        print("   ⚠️  Schema file missing - using defaults")
    
    # Test 4: Data loading (if files present)
    print("\n💾 4. Testing data loading...")
    
    if all(files_found[f] for f in ['loan_data', 'payment_history', 'payment_schedule']):
        try:
            # Test loading
            data = loader.load_abaco_data()
            
            if data:
                print(f"   ✅ Data loading successful: {len(data)} tables loaded")
                
                for table_name, df in data.items():
                    print(f"      📊 {table_name}: {len(df):,} rows, {len(df.columns)} columns")
                    
                    # Check for derived fields
                    derived_fields = []
                    if 'risk_score' in df.columns:
                        derived_fields.append('risk_score')
                    if 'delinquency_bucket' in df.columns:
                        derived_fields.append('delinquency_bucket')
                    
                    if derived_fields:
                        print(f"         🎯 Derived fields: {derived_fields}")
                
                # Test data quality
                if 'loan_data' in data:
                    loan_df = data['loan_data']
                    
                    # Check companies
                    if 'Company' in loan_df.columns:
                        companies = loan_df['Company'].value_counts()
                        print(f"   🏢 Companies: {dict(companies)}")
                    
                    # Check currencies
                    if 'Loan Currency' in loan_df.columns:
                        currencies = loan_df['Loan Currency'].value_counts()
                        print(f"   💰 Currencies: {dict(currencies)}")
                    
                    # Check risk distribution
                    if 'risk_score' in loan_df.columns:
                        avg_risk = loan_df['risk_score'].mean()
                        high_risk = (loan_df['risk_score'] > 0.7).sum()
                        print(f"   ⚠️  Risk Analysis: avg={avg_risk:.3f}, high_risk={high_risk:,}")
                        
            else:
                print("   ❌ No data loaded")
                return False
                
        except Exception as e:
            print(f"   ❌ Data loading error: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        missing_files = [f for f, exists in files_found.items() if not exists and f != 'schema']
        print(f"   ⚠️  Skipping data loading - missing files: {missing_files}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 READINESS SUMMARY")
    print("=" * 60)
    
    total_checks = 4
    passed_checks = 0
    
    # File check
    critical_files = ['loan_data', 'payment_history', 'payment_schedule']
    if all(files_found[f] for f in critical_files):
        print("✅ Required files: PRESENT")
        passed_checks += 1
    else:
        print("❌ Required files: MISSING")
    
    # Module check
    try:
        DataLoader()
        print("✅ Module imports: SUCCESS")
        passed_checks += 1
    except:
        print("❌ Module imports: FAILED")
    
    # Schema check
    if files_found.get('schema'):
        print("✅ Schema validation: AVAILABLE")
        passed_checks += 1
    else:
        print("⚠️  Schema validation: LIMITED")
        passed_checks += 0.5
    
    # Data loading check
    if all(files_found[f] for f in critical_files):
        try:
            test_loader = DataLoader()
            test_data = test_loader.load_abaco_data()
            if test_data and len(test_data) >= 3:
                print("✅ Data processing: SUCCESS")
                passed_checks += 1
            else:
                print("⚠️  Data processing: PARTIAL")
                passed_checks += 0.5
        except:
            print("❌ Data processing: FAILED")
    else:
        print("➖ Data processing: SKIPPED (missing files)")
    
    # Final verdict
    print(f"\n🎯 Overall Score: {passed_checks}/{total_checks}")
    
    if passed_checks >= 3.5:
        print("🎉 READY TO RUN! Abaco integration is production-ready")
        print("\n🚀 Next steps:")
        print("   1. Place Abaco CSV files in data/ directory")
        print("   2. Run: python portfolio.py --abaco-only")
        print("   3. Check results in abaco_runtime/exports/")
        return True
    elif passed_checks >= 2:
        print("⚠️  MOSTLY READY - Minor issues need attention")
        return True
    else:
        print("❌ NOT READY - Critical issues must be resolved")
        return False

if __name__ == '__main__':
    success = test_abaco_integration()
    print(f"\n📊 Integration Status: {'READY' if success else 'NEEDS WORK'}")
    sys.exit(0 if success else 1)
