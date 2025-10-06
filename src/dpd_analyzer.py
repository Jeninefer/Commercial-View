"""
DPD analyzer module extracted from PRs #31-40
Advanced DPD calculation and bucket assignment
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class DPDAnalyzer:
    """Advanced DPD analysis with bucket assignment capabilities"""

    def __init__(self):
        self.dpd_buckets = {
            "current": (0, 0),
            "1_30": (1, 30),
            "31_60": (31, 60),
            "61_90": (61, 90),
            "90_plus": (91, float("inf")),
        }

    def assign_dpd_buckets(
        self, df: pd.DataFrame, dpd_column: str = "days_past_due"
    ) -> pd.DataFrame:
        """Assign DPD buckets based on days past due"""
        result_df = df.copy()

        def get_bucket(dpd_value):
            if pd.isna(dpd_value):
                return "unknown"
            for bucket_name, (min_days, max_days) in self.dpd_buckets.items():
                if min_days <= dpd_value <= max_days:
                    return bucket_name
            return "unknown"

        result_df["dpd_bucket"] = result_df[dpd_column].apply(get_bucket)
        logger.info(f"DPD buckets assigned for {len(result_df)} records")
        return result_df

    def calculate_accurate_dpd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate accurate DPD based on current arrears status"""
        result_df = df.copy()

        if "due_date" in result_df.columns and "current_date" in result_df.columns:
            result_df["due_date"] = pd.to_datetime(result_df["due_date"])
            result_df["current_date"] = pd.to_datetime(result_df["current_date"])
            result_df["days_past_due"] = (
                result_df["current_date"] - result_df["due_date"]
            ).dt.days
            result_df["days_past_due"] = result_df["days_past_due"].clip(lower=0)

        return result_df


if __name__ == "__main__":
    print("DPDAnalyzer module loaded successfully")
    analyzer = DPDAnalyzer()
    print(f"Available DPD buckets: {list(analyzer.dpd_buckets.keys())}")
