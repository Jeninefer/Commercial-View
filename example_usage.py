#!/usr/bin/env python3
"""
Example usage of the MetricsRegistry class.
This script demonstrates all the key features of the MetricsRegistry.
"""

import time
import pandas as pd
from metrics_registry import MetricsRegistry


def main():
    print("=" * 60)
    print("MetricsRegistry Example Usage")
    print("=" * 60)
    
    # Initialize the registry
    registry = MetricsRegistry()
    print("\n1. Initialized MetricsRegistry")
    
    # Example 1: Timer operations
    print("\n2. Testing timer operations...")
    registry.start_timer('data_processing')
    time.sleep(0.1)  # Simulate work
    latency = registry.end_timer('data_processing')
    print(f"   Operation took: {latency:.4f} seconds")
    
    # Example 2: Recording custom metrics
    print("\n3. Recording custom metrics...")
    registry.record_metric('api_calls', 150, {'endpoint': '/api/data'})
    registry.record_metric('api_calls', 200, {'endpoint': '/api/users'})
    print("   Recorded 2 API call metrics")
    
    # Example 3: Data quality metrics
    print("\n4. Analyzing data quality...")
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'revenue': [100.5, 200.0, None, 150.75, 300.0],
        'region': ['North', 'South', 'East', None, 'West']
    })
    registry.record_data_metrics(df, 'customer_analysis')
    print(f"   Analyzed DataFrame with {len(df)} rows and {len(df.columns)} columns")
    
    # Example 4: Recording rules evaluated
    print("\n5. Recording validation rules...")
    registry.record_rules_evaluated(25, 'data_validation')
    print("   Recorded 25 validation rules")
    
    # Example 5: Get latest metrics
    print("\n6. Retrieving latest metrics...")
    latest = registry.get_latest_metrics(hours_back=24)
    for metric_name, stats in latest.items():
        print(f"\n   {metric_name}:")
        for key, value in stats.items():
            print(f"     {key}: {value}")
    
    # Example 6: Export metrics
    print("\n7. Exporting metrics to file...")
    registry.export_metrics('/tmp/metrics_export.json')
    print("   Metrics exported to /tmp/metrics_export.json")
    
    # Example 7: Clear old metrics
    print("\n8. Clearing old metrics...")
    initial_count = sum(len(v) for v in registry.metrics.values())
    registry.clear_old_metrics(hours_to_keep=168)  # Keep last 7 days
    final_count = sum(len(v) for v in registry.metrics.values())
    print(f"   Metrics count: {initial_count} -> {final_count}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
