"""
Example usage of the DPD Analyzer
"""

import pandas as pd
from dpd_analyzer import DPDAnalyzer


def main():
    """Demonstrate the DPD Analyzer functionality."""
    
    # Create sample data
    print("=" * 60)
    print("DPD Analyzer Example")
    print("=" * 60)
    
    # Sample data with various DPD values
    sample_data = pd.DataFrame({
        "account_id": ["ACC001", "ACC002", "ACC003", "ACC004", "ACC005", "ACC006", "ACC007", "ACC008"],
        "days_past_due": [0, 15, 45, 75, 100, 135, 165, 200],
        "balance": [1000, 5000, 3000, 2000, 4000, 1500, 2500, 3500]
    })
    
    print("\nOriginal Data:")
    print(sample_data.to_string(index=False))
    
    # Initialize analyzer
    analyzer = DPDAnalyzer(dpd_threshold=90)
    
    # Assign DPD buckets
    result = analyzer.assign_dpd_buckets(sample_data)
    
    print("\n\nData with DPD Buckets:")
    print(result[["account_id", "days_past_due", "dpd_bucket", "dpd_bucket_description", "default_flag"]].to_string(index=False))
    
    # Demonstrate field detection
    print("\n" + "=" * 60)
    print("Field Detection Example")
    print("=" * 60)
    
    # Create a DataFrame with various column names
    df_with_columns = pd.DataFrame(columns=[
        "account_number", 
        "total_days_past_due", 
        "outstanding_balance",
        "customer_name"
    ])
    
    print("\nDataFrame columns:", list(df_with_columns.columns))
    
    # Try to detect different fields
    patterns_to_test = [
        ["days_past_due", "dpd", "days"],
        ["account", "acc"],
        ["balance", "amount"],
        ["customer", "client"]
    ]
    
    print("\nField Detection Results:")
    for patterns in patterns_to_test:
        detected = analyzer.detect_field(df_with_columns, patterns)
        print(f"  Patterns {patterns} -> Detected: {detected}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("DPD Analysis Summary")
    print("=" * 60)
    
    print(f"\nTotal accounts: {len(result)}")
    print(f"Accounts in default: {result['default_flag'].sum()}")
    print(f"Default rate: {result['default_flag'].sum() / len(result) * 100:.1f}%")
    
    print("\nAccounts by DPD Bucket:")
    bucket_counts = result['dpd_bucket'].value_counts().sort_index()
    for bucket, count in bucket_counts.items():
        print(f"  {bucket:15s}: {count}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
