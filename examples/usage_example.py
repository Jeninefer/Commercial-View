"""
Example usage of Commercial View KPI Calculator.

This script demonstrates how to use the various KPI calculation functions
to analyze a loan portfolio.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
from datetime import datetime, timedelta

from commercial_view import (
    KPIConfig,
    calculate_comprehensive_kpis,
    calculate_exposure_metrics,
    calculate_yield_metrics,
    calculate_delinquency_metrics,
    calculate_utilization_metrics,
    calculate_segment_mix_metrics,
    calculate_vintage_metrics,
)


def create_sample_loan_data():
    """Create sample loan portfolio data."""
    base_date = datetime(2020, 1, 1)
    
    loan_data = {
        'loan_id': [f'L{i:04d}' for i in range(1, 101)],
        'balance': [1000 + i * 100 for i in range(100)],
        'principal': [900 + i * 90 for i in range(100)],
        'outstanding_amount': [100 + i * 10 for i in range(100)],
        'interest_rate': [5.0 + (i % 10) * 0.5 for i in range(100)],
        'interest_income': [50 + i * 2 for i in range(100)],
        'delinquent': [1 if i % 5 == 0 else 0 for i in range(100)],
        'days_past_due': [0 if i % 5 != 0 else (i % 4) * 30 for i in range(100)],
        'credit_limit': [2000 + i * 150 for i in range(100)],
        'segment': ['retail' if i % 3 == 0 else 'commercial' if i % 3 == 1 else 'corporate' for i in range(100)],
        'product_type': ['term_loan' if i % 2 == 0 else 'line_of_credit' for i in range(100)],
        'loan_age': [365 + i * 10 for i in range(100)],
        'origination_date': [base_date + timedelta(days=i * 10) for i in range(100)],
        'maturity_date': [base_date + timedelta(days=1825 + i * 20) for i in range(100)],
    }
    
    return pd.DataFrame(loan_data)


def main():
    """Main function to demonstrate KPI calculations."""
    print("=" * 80)
    print("Commercial View KPI Calculator - Example Usage")
    print("=" * 80)
    print()
    
    # Create sample data
    print("Creating sample loan portfolio data...")
    loan_df = create_sample_loan_data()
    print(f"Created portfolio with {len(loan_df)} loans")
    print()
    
    # Example 1: Calculate all KPIs with default configuration
    print("-" * 80)
    print("Example 1: Calculate all KPIs with default configuration")
    print("-" * 80)
    
    all_kpis = calculate_comprehensive_kpis(loan_df)
    
    print("\nExposure Metrics:")
    for key, value in all_kpis['exposure_metrics'].items():
        print(f"  {key}: {value:,.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\nYield Metrics:")
    for key, value in all_kpis['yield_metrics'].items():
        print(f"  {key}: {value:,.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\nDelinquency Metrics:")
    for key, value in all_kpis['delinquency_metrics'].items():
        print(f"  {key}: {value:,.2f}" if isinstance(value, (float, int)) else f"  {key}: {value}")
    
    print("\nMetadata:")
    for key, value in all_kpis['metadata'].items():
        print(f"  {key}: {value}")
    
    # Example 2: Calculate specific metric groups
    print("\n" + "-" * 80)
    print("Example 2: Calculate specific metric groups")
    print("-" * 80)
    
    exposure = calculate_exposure_metrics(loan_df)
    print(f"\nTotal Portfolio Balance: ${exposure['total_balance']:,.2f}")
    print(f"Average Loan Balance: ${exposure['average_balance']:,.2f}")
    
    delinquency = calculate_delinquency_metrics(loan_df)
    print(f"\nDelinquency Rate: {delinquency['delinquency_rate']:.2f}%")
    print(f"Delinquent Count: {delinquency['delinquent_count']}")
    
    utilization = calculate_utilization_metrics(loan_df)
    print(f"\nPortfolio Utilization Rate: {utilization['portfolio_utilization_rate']:.2f}%")
    print(f"Average Utilization Rate: {utilization['average_utilization_rate']:.2f}%")
    
    # Example 3: Custom configuration
    print("\n" + "-" * 80)
    print("Example 3: Calculate KPIs with custom configuration")
    print("-" * 80)
    
    config = KPIConfig(
        include_exposure_metrics=True,
        include_yield_metrics=True,
        include_delinquency_metrics=False,
        include_metadata=False,
    )
    
    custom_kpis = calculate_comprehensive_kpis(loan_df, config)
    print(f"\nIncluded metric groups: {list(custom_kpis.keys())}")
    
    # Example 4: Segment analysis
    print("\n" + "-" * 80)
    print("Example 4: Segment Mix Analysis")
    print("-" * 80)
    
    segment_mix = calculate_segment_mix_metrics(loan_df)
    
    print("\nSegment Distribution by Count:")
    for key, value in segment_mix.items():
        if key.endswith('_count') and key.startswith('segment_'):
            segment_name = key.replace('segment_', '').replace('_count', '')
            pct_key = f'segment_{segment_name}_pct'
            pct = segment_mix.get(pct_key, 0)
            print(f"  {segment_name}: {value} loans ({pct:.1f}%)")
    
    print("\nProduct Type Distribution:")
    for key, value in segment_mix.items():
        if key.endswith('_count') and key.startswith('product_'):
            product_name = key.replace('product_', '').replace('_count', '')
            pct_key = f'product_{product_name}_pct'
            pct = segment_mix.get(pct_key, 0)
            print(f"  {product_name}: {value} loans ({pct:.1f}%)")
    
    # Example 5: Vintage analysis
    print("\n" + "-" * 80)
    print("Example 5: Vintage Analysis")
    print("-" * 80)
    
    vintage = calculate_vintage_metrics(loan_df)
    
    print(f"\nAverage Loan Age: {vintage['average_loan_age']:.0f} days")
    print(f"Median Loan Age: {vintage['median_loan_age']:.0f} days")
    print(f"Earliest Origination: {vintage['earliest_origination']}")
    print(f"Latest Origination: {vintage['latest_origination']}")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == '__main__':
    main()
