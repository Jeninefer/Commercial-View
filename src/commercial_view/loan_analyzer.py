"""Loan analyzer module for DPD bucket assignment and analysis."""

import numpy as np
import pandas as pd
from . import registry


class LoanAnalyzer:
    """Analyzes loan portfolios and assigns DPD buckets."""
    
    def __init__(self, config: dict = None, dpd_threshold: int = 90):
        """
        Initialize the LoanAnalyzer.
        
        Args:
            config: Optional configuration dictionary that may contain 'dpd_buckets'
            dpd_threshold: Days past due threshold for default flag (default: 90)
        """
        self.config = config or {}
        self.dpd_threshold = dpd_threshold
    
    def assign_dpd_buckets(self, dpd_df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign standard DPD buckets to loans.

        Uses optional self.config["dpd_buckets"] as a list of (low, high, label):
          [(0,0,"Current"), (1,29,"1-29"), (30,59,"30-59"), ..., (180,None,"180+")]
        When high=None, the bucket is open-ended.
        """
        if not isinstance(dpd_df, pd.DataFrame) or "days_past_due" not in dpd_df.columns:
            raise ValueError("dpd_df must contain 'days_past_due'")

        df = dpd_df.copy()
        dpd = pd.to_numeric(df["days_past_due"], errors="coerce").fillna(0)

        cfg = self.config.get("dpd_buckets", None)
        if cfg:
            out = pd.Series(index=df.index, dtype="object")
            last_label = None
            for low, high, label in cfg:
                last_label = label
                if high is None:
                    mask = dpd >= low
                else:
                    mask = (dpd >= low) & (dpd <= high)
                out[mask] = label
            df["dpd_bucket"] = out.fillna(last_label).astype(str)
        else:
            # Defaults: 0, 1–29, 30–59, 60–89, 90–119, 120–149, 150–179, 180+
            bins   = [-np.inf, 0, 29, 59, 89, 119, 149, 179, np.inf]
            labels = ["Current", "1-29", "30-59", "60-89", "90-119", "120-149", "150-179", "180+"]
            df["dpd_bucket"] = pd.cut(dpd, bins=bins, labels=labels, right=True, include_lowest=True).astype(str)

        df["default_flag"] = (dpd >= int(self.dpd_threshold)).astype(int)

        # Optional: quick quality metrics if registry is available
        try:
            registry.record_data_metrics(df, operation="assign_dpd_buckets")
        except Exception:
            pass

        return df
