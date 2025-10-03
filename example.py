#!/usr/bin/env python
"""Example usage of the KPI Exporter."""

import logging
from datetime import datetime

from src.kpi_exporter import KPIExporter

# Configure logging to see the export messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """Demonstrate KPI export functionality."""
    # Create an exporter instance
    exporter = KPIExporter(export_path="exports")
    
    # Example 1: Simple KPI data
    kpi_data = {
        "metric": "revenue",
        "value": 150000,
        "currency": "USD",
        "period": "Q4 2023"
    }
    
    filepath1 = exporter._export_json(kpi_data, "revenue_kpi")
    print(f"Exported: {filepath1}")
    
    # Example 2: Complex nested KPI data
    complex_kpi = {
        "company": "Commercial-View Inc",
        "metrics": {
            "revenue": {
                "q1": 100000,
                "q2": 120000,
                "q3": 135000,
                "q4": 150000
            },
            "customers": {
                "total": 5000,
                "new": 1200,
                "retained": 3800
            }
        },
        "timestamp": datetime(2023, 12, 31, 23, 59, 59),
        "status": "final"
    }
    
    filepath2 = exporter._export_json(complex_kpi, "annual_report")
    print(f"Exported: {filepath2}")
    
    print("\n✓ KPI export demonstration completed successfully!")

if __name__ == "__main__":
    main()
