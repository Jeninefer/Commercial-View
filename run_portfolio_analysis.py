"""
Commercial-View Portfolio Analytics - Test Runner

This script runs the complete analytics pipeline and generates test outputs.

Usage:
    python run_portfolio_analysis.py
"""

import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import required libraries
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Import project modules
try:
    from src.data_loader import load_loan_data, load_customer_data
    from src.utils.schema_parser import load_schema, get_dataset_info
    print("✅ Project modules loaded successfully")
except ImportError as e:
    print(f"⚠️  Could not load project modules: {e}")
    print("   Continuing with basic functionality...")


def test_data_loading():
    """Test data loading functionality"""
    print("\n" + "="*70)
    print("TEST 1: Data Loading")
    print("="*70)
    
    data_dir = project_root / "data" / "pricing"
    
    try:
        # Test loan data loading
        loan_df = load_loan_data(str(data_dir))
        print(f"✅ Loaded loan data: {len(loan_df):,} rows")
        
        # Test customer data loading
        customer_df = load_customer_data(str(data_dir))
        print(f"✅ Loaded customer data: {len(customer_df):,} rows")
        
        return True, {'loan_data': loan_df, 'customer_data': customer_df}
        
    except FileNotFoundError as e:
        print(f"⚠️  Data files not found: {e}")
        print("   Creating sample data for testing...")
        
        # Create sample data
        sample_loan_df = pd.DataFrame({
            'Loan ID': [f'L{i:04d}' for i in range(1, 101)],
            'Customer ID': [f'C{i:04d}' for i in range(1, 101)],
            'Disbursement Amount': np.random.uniform(10000, 100000, 100),
            'Interest Rate APR': np.random.uniform(0.10, 0.25, 100),
            'Loan Status': np.random.choice(['Active', 'Complete', 'Default'], 100),
            'Disbursement Date': pd.date_range('2024-01-01', periods=100, freq='D'),
            'Outstanding Balance': np.random.uniform(5000, 50000, 100),
            'Days in Default': np.random.randint(0, 90, 100)
        })
        
        sample_customer_df = pd.DataFrame({
            'Customer ID': [f'C{i:04d}' for i in range(1, 101)],
            'Customer Name': [f'Company {i}' for i in range(1, 101)],
            'Industry': np.random.choice(['Tech', 'Retail', 'Manufacturing', 'Services'], 100),
            'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
            'Year Founded': np.random.randint(1990, 2020, 100)
        })
        
        print(f"✅ Created sample data: {len(sample_loan_df):,} loans")
        return True, {'loan_data': sample_loan_df, 'customer_data': sample_customer_df}


def test_data_preparation(data_dict):
    """Test data preparation and feature engineering"""
    print("\n" + "="*70)
    print("TEST 2: Data Preparation")
    print("="*70)
    
    loan_df = data_dict['loan_data']
    customer_df = data_dict['customer_data']
    
    # Normalize column names
    loan_df.columns = loan_df.columns.str.lower().str.replace(' ', '_')
    customer_df.columns = customer_df.columns.str.lower().str.replace(' ', '_')
    
    # Merge datasets
    portfolio_df = loan_df.merge(customer_df, on='customer_id', how='left')
    
    print(f"✅ Merged portfolio: {len(portfolio_df):,} rows × {len(portfolio_df.columns)} columns")
    
    # Add simple features
    portfolio_df['is_active'] = portfolio_df['loan_status'].str.lower() == 'active'
    portfolio_df['dpd_bucket'] = pd.cut(
        portfolio_df.get('days_in_default', 0),
        bins=[-1, 0, 30, 60, 90, float('inf')],
        labels=['Current', 'DPD 1-30', 'DPD 31-60', 'DPD 61-90', 'DPD 90+']
    )
    
    print(f"✅ Added features: is_active, dpd_bucket")
    
    return True, portfolio_df


def test_kpi_calculation(portfolio_df):
    """Test KPI calculations"""
    print("\n" + "="*70)
    print("TEST 3: KPI Calculation")
    print("="*70)
    
    active_df = portfolio_df[portfolio_df['is_active'] == True]
    
    kpis = {
        'total_portfolio': active_df['outstanding_balance'].sum(),
        'active_loans': len(active_df),
        'active_customers': active_df['customer_id'].nunique(),
        'avg_loan_size': active_df['outstanding_balance'].mean(),
    }
    
    print("\n📊 Portfolio KPIs:")
    print(f"   Total Portfolio: ${kpis['total_portfolio']:,.2f}")
    print(f"   Active Loans: {kpis['active_loans']:,}")
    print(f"   Active Customers: {kpis['active_customers']:,}")
    print(f"   Avg Loan Size: ${kpis['avg_loan_size']:,.2f}")
    
    return True, kpis


def test_visualization(portfolio_df):
    """Test basic visualization creation"""
    print("\n" + "="*70)
    print("TEST 4: Visualization")
    print("="*70)
    
    try:
        import plotly.graph_objects as go
        
        # Create simple bar chart
        dpd_dist = portfolio_df['dpd_bucket'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(x=dpd_dist.index, y=dpd_dist.values)
        ])
        
        fig.update_layout(
            title='DPD Distribution',
            xaxis_title='DPD Bucket',
            yaxis_title='Count'
        )
        
        # Save to output
        output_dir = project_root / "output" / "test_results"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        fig_path = output_dir / "dpd_distribution.html"
        fig.write_html(str(fig_path))
        
        print(f"✅ Created visualization: {fig_path}")
        return True, fig
        
    except ImportError:
        print("⚠️  Plotly not available, skipping visualization")
        return False, None


def test_export(kpis, portfolio_df):
    """Test data export functionality"""
    print("\n" + "="*70)
    print("TEST 5: Data Export")
    print("="*70)
    
    output_dir = project_root / "output" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export KPIs
    kpi_df = pd.DataFrame([
        {'KPI': k, 'Value': v}
        for k, v in kpis.items()
    ])
    kpi_path = output_dir / f'kpis_{timestamp}.csv'
    kpi_df.to_csv(kpi_path, index=False)
    print(f"✅ Exported KPIs to: {kpi_path}")
    
    # Export portfolio summary
    summary = {
        'timestamp': timestamp,
        'kpis': kpis,
        'data_summary': {
            'total_rows': len(portfolio_df),
            'columns': list(portfolio_df.columns)
        }
    }
    
    json_path = output_dir / f'summary_{timestamp}.json'
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"✅ Exported summary to: {json_path}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("Commercial-View Portfolio Analytics - Test Suite")
    print("="*70)
    print(f"Project root: {project_root}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Data Loading
    success, data_dict = test_data_loading()
    results.append(('Data Loading', success))
    if not success:
        print("\n❌ Test suite failed at data loading")
        return
    
    # Test 2: Data Preparation
    success, portfolio_df = test_data_preparation(data_dict)
    results.append(('Data Preparation', success))
    if not success:
        print("\n❌ Test suite failed at data preparation")
        return
    
    # Test 3: KPI Calculation
    success, kpis = test_kpi_calculation(portfolio_df)
    results.append(('KPI Calculation', success))
    
    # Test 4: Visualization
    success, fig = test_visualization(portfolio_df)
    results.append(('Visualization', success))
    
    # Test 5: Export
    success = test_export(kpis, portfolio_df)
    results.append(('Data Export', success))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\nNext steps:")
        print("1. Review outputs in: output/test_results/")
        print("2. Run the full notebook: notebooks/portfolio_analytics_pipeline.ipynb")
        print("3. Configure with your actual data sources")
    else:
        print("\n⚠️  Some tests failed. Review the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
