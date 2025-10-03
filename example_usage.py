#!/usr/bin/env python3
"""
Example usage of the MetricsRegistry class.
"""

import pandas as pd
import time
from metrics_registry import MetricsRegistry


def main():
    # Initialize the registry
    registry = MetricsRegistry()
    
    print("=== MetricsRegistry Demo ===\n")
    
    # 1. Timer operations
    print("1. Testing timer operations...")
    registry.start_timer('data_processing')
    time.sleep(0.1)  # Simulate some work
    latency = registry.end_timer('data_processing')
    print(f"   Operation took {latency:.3f} seconds\n")
    
    # 2. Record custom metrics
    print("2. Recording custom metrics...")
    registry.record_metric('temperature', 72.5, {'location': 'server_room'})
    registry.record_metric('requests', 1500, {'endpoint': '/api/data'})
    print("   Custom metrics recorded\n")
    
    # 3. Record data quality metrics
    print("3. Recording data quality metrics...")
    df = pd.DataFrame({
        'sales': [100, 200, None, 400, 500],
        'region': ['North', 'South', 'East', 'West', 'Central'],
        'profit': [10, 20, 30, None, 50]
    })
    registry.record_data_metrics(df, 'sales_data')
    print(f"   Analyzed DataFrame with {len(df)} rows and {len(df.columns)} columns\n")
    
    # 4. Record validation rules
    print("4. Recording validation rules...")
    registry.record_rules_evaluated(15, 'data_validation')
    print("   Recorded 15 validation rules evaluated\n")
    
    # 5. Get latest metrics
    print("5. Getting latest metrics (last 24 hours)...")
    latest = registry.get_latest_metrics(hours_back=24)
    for metric_name, stats in latest.items():
        print(f"   {metric_name}:")
        for key, value in stats.items():
            print(f"     - {key}: {value}")
    print()
    
    # 6. Export metrics to file
    print("6. Exporting metrics to file...")
    registry.export_metrics('/tmp/metrics_export.json')
    print("   Metrics exported to /tmp/metrics_export.json\n")
    
    # 7. Show current metrics count
    print("7. Current metrics summary:")
    for metric_name, records in registry.metrics.items():
        print(f"   - {metric_name}: {len(records)} record(s)")
    
    print("\n=== Demo Complete ===")


if __name__ == '__main__':
    main()
