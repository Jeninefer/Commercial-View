#!/usr/bin/env python3
"""
Test and fix script for feature_engineer module
"""

import os
import sys
import traceback

import pandas as pd

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def main() -> int:
    try:
        from feature_engineer import FeatureEngineer  # type: ignore
    except ImportError as err:
        print(f"❌ Import error: {err}")
        return 1

    try:
        fe = FeatureEngineer()
        print("✅ FeatureEngineer instantiated successfully")

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

        portfolio_path = "data/processed/portfolio_with_features.csv"
        cohort_retention_path = "data/processed/cohort_retention_matrix.csv"

        if os.path.exists(portfolio_path) and os.path.exists(cohort_retention_path):
            portfolio_data = pd.read_csv(portfolio_path)
            print(f"✅ Portfolio data loaded: {len(portfolio_data)} rows")

            cohort_retention = pd.read_csv(cohort_retention_path)
            print(f"✅ Cohort retention matrix loaded: {len(cohort_retention)} rows")

            if "cohort" in result.columns:
                result = result.merge(cohort_retention, on="cohort", how="left")
                print("✅ Cohort retention matrix merged into result")
            else:
                print("⚠️ Result lacks 'cohort' column; skipping merge")
        else:
            print("⚠️ Optional data files not found; skipping merge tests")

    except Exception as err:
        print(f"❌ Error during FeatureEngineer tests: {err}")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
