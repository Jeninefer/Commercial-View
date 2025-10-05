#!/usr/bin/env python3
"""
Test script for feature_engineer module
"""

import os
import sys

src_path = os.path.join(os.path.dirname(__file__), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from feature_engineer import FeatureEngineer

print("✅ FeatureEngineer imported successfully")

# Test instantiation
fe = FeatureEngineer()
print("✅ FeatureEngineer instantiated successfully")

# Test basic functionality
import pandas as pd

sample_data = pd.DataFrame(
    {
        "customer_id": range(5),
        "loan_count": [1, 2, 3, 1, 2],
        "last_active_date": pd.date_range("2023-01-01", periods=5),
    }
)

result = fe.classify_client_type(sample_data)
print(f"✅ classify_client_type worked: {len(result)} rows")
print(f"✅ Customer types: {result['customer_type'].value_counts().to_dict()}")
