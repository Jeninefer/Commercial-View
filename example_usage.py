"""
Example demonstrating the DPD Bucket Classification System.

This script shows how to use both PaymentProcessor and FeatureEngineer
to classify loans and understand the difference between accounting default
(180+ days) and high risk (90+ days) thresholds.
"""

import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from payment_processor import PaymentProcessor
from feature_engineer import FeatureEngineer


def create_sample_portfolio():
    """Create a sample loan portfolio with various DPD values."""
    return pd.DataFrame({
        'loan_id': ['L001', 'L002', 'L003', 'L004', 'L005', 'L006', 'L007', 'L008', 'L009', 'L010'],
        'borrower': ['Company A', 'Company B', 'Company C', 'Company D', 'Company E', 
                    'Company F', 'Company G', 'Company H', 'Company I', 'Company J'],
        'amount': [100000, 250000, 75000, 150000, 500000, 80000, 120000, 300000, 90000, 200000],
        'days_past_due': [5, 45, 75, 95, 125, 150, 185, 220, 89, 180]
    })


def analyze_with_payment_processor(df):
    """Analyze loans using PaymentProcessor (accounting perspective)."""
    print("\n" + "="*80)
    print("PAYMENT PROCESSOR ANALYSIS (Accounting Default: 180+ Days)")
    print("="*80)
    
    processor = PaymentProcessor()
    result = processor.assign_dpd_buckets(df.copy())
    
    # Summary statistics
    print(f"\nDPD Threshold: {processor.dpd_threshold} days")
    print(f"Total loans: {len(result)}")
    print(f"Loans in default (>= {processor.dpd_threshold} days): {result['default_flag'].sum()}")
    print(f"Total exposure in default: ${result[result['default_flag']]['amount'].sum():,.2f}")
    
    # Bucket distribution
    print("\nBucket Distribution:")
    bucket_summary = result.groupby('dpd_bucket').agg({
        'loan_id': 'count',
        'amount': 'sum',
        'default_flag': 'sum'
    }).rename(columns={'loan_id': 'count', 'amount': 'total_exposure'})
    print(bucket_summary)
    
    # Default loans detail
    print("\nLoans in Default Status (>= 180 days):")
    default_loans = result[result['default_flag']][['loan_id', 'borrower', 'amount', 'days_past_due', 'dpd_bucket_description']]
    if len(default_loans) > 0:
        print(default_loans.to_string(index=False))
    else:
        print("No loans in default status")
    
    return result


def analyze_with_feature_engineer(df):
    """Analyze loans using FeatureEngineer (risk perspective)."""
    print("\n" + "="*80)
    print("FEATURE ENGINEER ANALYSIS (High Risk: 90+ Days)")
    print("="*80)
    
    engineer = FeatureEngineer()
    result = engineer.assign_dpd_buckets(df.copy())
    
    # Summary statistics
    print(f"\nRisk Threshold: {engineer.risk_threshold} days")
    print(f"Total loans: {len(result)}")
    print(f"Loans flagged as high risk (>= {engineer.risk_threshold} days): {result['is_default'].sum()}")
    print(f"Total exposure at high risk: ${result[result['is_default']]['amount'].sum():,.2f}")
    
    # Risk category distribution
    print("\nRisk Category Distribution:")
    risk_summary = result.groupby('dpd_risk_category').agg({
        'loan_id': 'count',
        'amount': 'sum',
        'is_default': 'sum'
    }).rename(columns={'loan_id': 'count', 'amount': 'total_exposure'})
    print(risk_summary)
    
    # High risk loans detail
    print("\nLoans Flagged for Risk Analysis (>= 90 days):")
    high_risk_loans = result[result['is_default']][['loan_id', 'borrower', 'amount', 'days_past_due', 'dpd_risk_category']]
    if len(high_risk_loans) > 0:
        print(high_risk_loans.to_string(index=False))
    else:
        print("No loans flagged as high risk")
    
    return result


def compare_approaches(processor_result, engineer_result):
    """Compare the two approaches side by side."""
    print("\n" + "="*80)
    print("COMPARISON: ACCOUNTING DEFAULT vs HIGH RISK")
    print("="*80)
    
    comparison = pd.DataFrame({
        'loan_id': processor_result['loan_id'],
        'borrower': processor_result['borrower'],
        'amount': processor_result['amount'],
        'days_past_due': processor_result['days_past_due'],
        'dpd_bucket': processor_result['dpd_bucket'],
        'default_flag (180+)': processor_result['default_flag'],
        'is_default (90+)': engineer_result['is_default']
    })
    
    # Sort by days past due
    comparison = comparison.sort_values('days_past_due', ascending=False)
    
    print("\nSide-by-Side Comparison:")
    print(comparison.to_string(index=False))
    
    # Highlight the difference
    print("\n" + "-"*80)
    print("KEY INSIGHTS:")
    print("-"*80)
    
    # Loans in the 90-179 day range (High Risk but not Accounting Default)
    intervention_zone = comparison[
        (comparison['is_default (90+)'] == True) & 
        (comparison['default_flag (180+)'] == False)
    ]
    
    if len(intervention_zone) > 0:
        print(f"\nEarly Intervention Opportunities (90-179 days):")
        print(f"  - Count: {len(intervention_zone)} loans")
        print(f"  - Total exposure: ${intervention_zone['amount'].sum():,.2f}")
        print(f"  - These loans are HIGH RISK but not yet accounting defaults")
        print(f"  - Action: Priority for collection and workout strategies")
        print("\nLoans in this category:")
        print(intervention_zone[['loan_id', 'borrower', 'amount', 'days_past_due']].to_string(index=False))
    
    # Accounting defaults
    accounting_defaults = comparison[comparison['default_flag (180+)'] == True]
    if len(accounting_defaults) > 0:
        print(f"\nAccounting Defaults (180+ days):")
        print(f"  - Count: {len(accounting_defaults)} loans")
        print(f"  - Total exposure: ${accounting_defaults['amount'].sum():,.2f}")
        print(f"  - These loans require provisioning and potential charge-off")
    
    # Current and performing loans
    performing = comparison[comparison['is_default (90+)'] == False]
    print(f"\nPerforming Loans (<90 days):")
    print(f"  - Count: {len(performing)} loans")
    print(f"  - Total exposure: ${performing['amount'].sum():,.2f}")
    print(f"  - These loans are current or in early delinquency")


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("COMMERCIAL-VIEW: DPD BUCKET CLASSIFICATION DEMONSTRATION")
    print("="*80)
    
    # Create sample portfolio
    print("\nCreating sample loan portfolio...")
    portfolio = create_sample_portfolio()
    
    print("\nSample Portfolio:")
    print(portfolio.to_string(index=False))
    
    # Analyze with PaymentProcessor
    processor_result = analyze_with_payment_processor(portfolio)
    
    # Analyze with FeatureEngineer
    engineer_result = analyze_with_feature_engineer(portfolio)
    
    # Compare both approaches
    compare_approaches(processor_result, engineer_result)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
The DPD Bucket Classification System provides two complementary views:

1. PAYMENT PROCESSOR (Accounting Default: 180+ days)
   - Purpose: Financial reporting, regulatory compliance
   - Flag: default_flag = True for loans >= 180 days
   - Use case: Provisioning, charge-offs, external reporting

2. FEATURE ENGINEER (High Risk: 90+ days)
   - Purpose: Risk analysis, portfolio management
   - Flag: is_default = True for loans >= 90 days
   - Use case: Early intervention, collection strategies, risk monitoring

Both methods use consistent bucket labels but different thresholds to serve
their respective analytical needs. This allows organizations to:
- Meet regulatory requirements (180-day default)
- Proactively manage risk (90-day high risk threshold)
- Identify early intervention opportunities (90-179 day range)
    """)
    
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
