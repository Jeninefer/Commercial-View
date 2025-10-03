"""Example usage of MetricsRegistry for Commercial View KPI tracking."""

import sys
import os
import pandas as pd
import time

# Import MetricsRegistry from src package
from src.metrics_registry import MetricsRegistry
def main():
    """Demonstrate MetricsRegistry usage."""
    print("=== Commercial View - MetricsRegistry Example ===\n")
    
    # Initialize the registry
    registry = MetricsRegistry()
    
    # Example 1: Record simple metrics
    print("1. Recording simple metrics...")
    registry.record_metric("revenue", 50000.00, {"region": "North", "currency": "USD"})
    registry.record_metric("revenue", 75000.00, {"region": "South", "currency": "USD"})
    registry.record_metric("customer_count", 150, {"region": "North"})
    print("   ✓ Recorded revenue and customer count metrics\n")
    
    # Example 2: Time an operation
    print("2. Timing an operation...")
    registry.start_timer("data_processing")
    time.sleep(0.1)  # Simulate processing
    latency = registry.end_timer("data_processing")
    print(f"   ✓ Operation completed in {latency:.3f} seconds\n")
    
    # Example 3: Record data quality metrics
    print("3. Recording data quality metrics...")
    df = pd.DataFrame({
        'product': ['A', 'B', 'C', 'D', 'E'],
        'sales': [100, 200, None, 400, 500],
        'quantity': [10, 20, 30, None, 50]
    })
    registry.record_data_metrics(df, "sales_data")
    print(f"   ✓ Recorded metrics for DataFrame with {len(df)} rows\n")
    
    # Example 4: Record rules evaluated
    print("4. Recording validation rules...")
    registry.record_rules_evaluated(25, "data_validation")
    print("   ✓ Recorded 25 validation rules evaluated\n")
    
    # Example 5: Get latest metrics summary
    print("5. Latest metrics summary:")
    latest = registry.get_latest_metrics(hours_back=24)
    for metric_name, stats in latest.items():
        print(f"   {metric_name}:")
        print(f"      - Count: {stats['count']}")
        print(f"      - Latest: {stats['latest']}")
        if stats['avg'] is not None:
            print(f"      - Average: {stats['avg']:.2f}")
        if stats['min'] is not None:
            print(f"      - Min: {stats['min']}")
        if stats['max'] is not None:
            print(f"      - Max: {stats['max']}")
    print()
    
    # Example 6: Export metrics
    print("6. Exporting metrics...")
    output_file = "/tmp/commercial_view_metrics.json"
    registry.export_metrics(output_file)
    print(f"   ✓ Metrics exported to {output_file}\n")
    
    # Example 7: Clear old metrics
    print("7. Clearing old metrics...")
    initial_count = sum(len(v) for v in registry.metrics.values())
    registry.clear_old_metrics(hours_to_keep=168)  # Keep 1 week
    final_count = sum(len(v) for v in registry.metrics.values())
    print(f"   ✓ Kept {final_count} recent metrics (from {initial_count} total)\n")
    
    print("=== Example Complete ===")


if __name__ == "__main__":
    main()
