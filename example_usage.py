"""
Example usage of DPD Bucket Analyzer

This script demonstrates how to use the DPDBucketAnalyzer class
to classify Days Past Due data and calculate default flags.
"""

import pandas as pd
from dpd_analyzer import DPDBucketAnalyzer


def example_basic_usage():
    """Example 1: Basic usage with default buckets"""
    print("=" * 60)
    print("Example 1: Basic Usage with Default Buckets")
    print("=" * 60)
    
    # Create sample data
    data = {
        "account_id": [1, 2, 3, 4, 5, 6, 7, 8],
        "days_past_due": [0, 15, 45, 75, 100, 130, 165, 200]
    }
    df = pd.DataFrame(data)
    
    print("\nInput DataFrame:")
    print(df)
    
    # Create analyzer with default settings
    analyzer = DPDBucketAnalyzer(dpd_threshold=90)
    
    # Get DPD buckets
    result = analyzer.get_dpd_buckets(df)
    
    print("\nOutput DataFrame with DPD Buckets:")
    print(result)
    print("\n")


def example_custom_buckets():
    """Example 2: Custom bucket configuration"""
    print("=" * 60)
    print("Example 2: Custom Bucket Configuration")
    print("=" * 60)
    
    # Define custom buckets
    config = {
        "dpd_buckets": [
            (0, 0, "Current"),
            (1, 30, "1-30 Days"),
            (31, 60, "31-60 Days"),
            (61, 90, "61-90 Days"),
            (91, None, "90+ Days")
        ]
    }
    
    # Create sample data
    data = {
        "account_id": [101, 102, 103, 104, 105],
        "days_past_due": [0, 20, 50, 80, 150]
    }
    df = pd.DataFrame(data)
    
    print("\nInput DataFrame:")
    print(df)
    
    # Create analyzer with custom configuration
    analyzer = DPDBucketAnalyzer(config=config, dpd_threshold=90)
    
    # Get DPD buckets
    result = analyzer.get_dpd_buckets(df)
    
    print("\nOutput DataFrame with Custom Buckets:")
    print(result)
    print("\n")


def example_custom_threshold():
    """Example 3: Custom default threshold"""
    print("=" * 60)
    print("Example 3: Custom Default Threshold")
    print("=" * 60)
    
    # Create sample data
    data = {
        "account_id": [201, 202, 203, 204, 205],
        "days_past_due": [30, 45, 60, 75, 90]
    }
    df = pd.DataFrame(data)
    
    print("\nInput DataFrame:")
    print(df)
    
    # Create analyzer with custom threshold (60 days)
    analyzer = DPDBucketAnalyzer(dpd_threshold=60)
    
    # Get DPD buckets
    result = analyzer.get_dpd_buckets(df)
    
    print("\nOutput DataFrame (default threshold = 60 days):")
    print(result)
    print("\n")


def example_with_invalid_data():
    """Example 4: Handling invalid data"""
    print("=" * 60)
    print("Example 4: Handling Invalid Data")
    print("=" * 60)
    
    # Create sample data with invalid values
    data = {
        "account_id": [301, 302, 303, 304, 305],
        "days_past_due": [10, "invalid", None, 45, pd.NA]
    }
    df = pd.DataFrame(data)
    
    print("\nInput DataFrame (with invalid values):")
    print(df)
    
    # Create analyzer
    analyzer = DPDBucketAnalyzer()
    
    # Get DPD buckets (invalid values will be coerced to 0)
    result = analyzer.get_dpd_buckets(df)
    
    print("\nOutput DataFrame (invalid values treated as 0):")
    print(result)
    print("\n")


def main():
    """Run all examples"""
    print("\nDPD Bucket Analyzer - Example Usage\n")
    
    example_basic_usage()
    example_custom_buckets()
    example_custom_threshold()
    example_with_invalid_data()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
