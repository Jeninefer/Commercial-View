"""
DPD (Days Past Due) Bucket Analyzer Module

This module provides functionality to classify Days Past Due data into buckets
and calculate default flags for credit analysis.
"""

import numpy as np
import pandas as pd


class DataQualityRegistry:
    """
    Simple registry for recording data quality metrics.
    """
    
    def record_data_metrics(self, df: pd.DataFrame, operation: str = None) -> None:
        """
        Record basic data quality metrics for a dataframe.
        
        Args:
            df: The DataFrame to record metrics for
            operation: Optional name of the operation being performed
        """
        # Basic implementation - can be extended with more sophisticated metrics
        pass


# Global registry instance
registry = DataQualityRegistry()


class DPDBucketAnalyzer:
    """
    Analyzer for Days Past Due (DPD) bucketing and default flag calculation.
    
    This class provides methods to classify DPD values into buckets and
    calculate default flags based on configurable thresholds.
    """
    
    def __init__(self, config: dict = None, dpd_threshold: int = 90):
        """
        Initialize the DPD Bucket Analyzer.
        
        Args:
            config: Configuration dictionary that may contain 'dpd_buckets'
                   as a list of tuples: [(low, high, label), ...]
            dpd_threshold: Threshold for marking accounts as defaulted (default: 90)
        """
        self.config = config or {}
        self.dpd_threshold = dpd_threshold
    
    def get_dpd_buckets(self, dpd_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add DPD bucket classifications to the dataframe.

        Uses config["dpd_buckets"] if provided as a list of tuples:
          [(0,0,"Current"), (1,29,"1-29"), (30,59,"30-59"), ... , (180,None,"180+")]
        When upper is None it means open-ended.

        Args:
            dpd_df: DataFrame with a 'days_past_due' column

        Returns:
            DataFrame with 'dpd_bucket' and 'default_flag' columns added
        """
        if "days_past_due" not in dpd_df.columns:
            raise ValueError("Column 'days_past_due' is required to bucket DPD")

        df = dpd_df.copy()
        dpd = pd.to_numeric(df["days_past_due"], errors="coerce").fillna(0)

        # Configurable buckets or sane defaults
        cfg_buckets = self.config.get("dpd_buckets")
        if cfg_buckets:
            # Validate and build edges/labels
            edges = []
            labels = []
            for low, high, label in cfg_buckets:
                if high is None:
                    edges.append((low, np.inf))
                else:
                    edges.append((low, high))
                labels.append(label)
            # Convert to boundaries for pd.cut
            # Example: [(0,0),(1,29),...,(180,inf)]
            # Map each interval to label
            # Assign bucket labels by iterating over each interval and setting the label for matching DPD values
            bucket_series = pd.Series(index=df.index, dtype="object")
            for (low, high), label in zip(edges, labels):
                mask = (dpd >= low) & (dpd <= high)
                mask = (dpd >= low) & ((dpd <= high) if not np.isinf(high) else True)
        else:
            # Defaults: 0, 1–29, 30–59, 60–89, 90–119, 120–149, 150–179, 180+
            bins   = [-np.inf, 0, 29, 59, 89, 119, 149, 179, np.inf]
            labels = ["Current", "1-29", "30-59", "60-89", "90-119", "120-149", "150-179", "180+"]
            bucket_series = pd.cut(dpd, bins=bins, labels=labels, right=True, include_lowest=True)

        df["dpd_bucket"] = bucket_series.astype(str)

        # Default flag using analyzer threshold
        df["default_flag"] = (dpd >= int(self.dpd_threshold)).astype(int)

        # Optional: basic quality metrics (requires global `registry`)
        try:
            registry.record_data_metrics(df, operation="dpd_bucketing")
        except Exception:
            pass

        return df
