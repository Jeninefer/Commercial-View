"""Example usage of LoanAnalyzer for DPD bucket assignment."""

import pandas as pd
from src.commercial_view import LoanAnalyzer


def main():
    """Demonstrate LoanAnalyzer functionality."""
    
    # Example 1: Using default DPD buckets
    print("=" * 60)
    print("Example 1: Default DPD Buckets")
    print("=" * 60)
    
    analyzer = LoanAnalyzer(dpd_threshold=90)
    
    # Create sample loan data
    df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'loan_amount': [10000, 25000, 50000, 15000, 30000, 20000, 45000, 35000],
        'days_past_due': [0, 15, 35, 65, 95, 125, 165, 195]
    })
    
    print("\nOriginal Data:")
    print(df)
    
    result = analyzer.assign_dpd_buckets(df)
    
    print("\nData with DPD Buckets and Default Flags:")
    print(result)
    
    print("\nSummary by DPD Bucket:")
    print(result.groupby('dpd_bucket').agg({
        'loan_id': 'count',
        'loan_amount': 'sum',
        'default_flag': 'sum'
    }).rename(columns={'loan_id': 'count', 'loan_amount': 'total_amount', 'default_flag': 'defaults'}))
    
    # Example 2: Using custom DPD buckets
    print("\n" + "=" * 60)
    print("Example 2: Custom DPD Buckets")
    print("=" * 60)
    
    custom_config = {
        "dpd_buckets": [
            (0, 0, "Current"),
            (1, 29, "Early Delinquency"),
            (30, 89, "Moderate Delinquency"),
            (90, 179, "Severe Delinquency"),
            (180, None, "Default")
        ]
    }
    
    custom_analyzer = LoanAnalyzer(config=custom_config, dpd_threshold=90)
    
    result2 = custom_analyzer.assign_dpd_buckets(df)
    
    print("\nData with Custom DPD Buckets:")
    print(result2[['loan_id', 'days_past_due', 'dpd_bucket', 'default_flag']])
    
    print("\nSummary by Custom DPD Bucket:")
    print(result2.groupby('dpd_bucket').agg({
        'loan_id': 'count',
        'loan_amount': 'sum'
    }).rename(columns={'loan_id': 'count', 'loan_amount': 'total_amount'}))
    
    # Example 3: Handling edge cases
    print("\n" + "=" * 60)
    print("Example 3: Edge Cases (NaN, invalid values)")
    print("=" * 60)
    
    edge_df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'loan_amount': [10000, 15000, 20000, 25000],
        'days_past_due': [0, 'N/A', None, 45]
    })
    
    print("\nOriginal Data with Invalid Values:")
    print(edge_df)
    
    result3 = analyzer.assign_dpd_buckets(edge_df)
    
    print("\nProcessed Data (invalid values coerced to 0):")
    print(result3)


if __name__ == "__main__":
    main()
