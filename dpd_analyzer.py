"""
DPD (Days Past Due) Analyzer Module

This module provides functionality for analyzing days past due data
and assigning appropriate buckets and flags for loan portfolio analysis.
"""

import re
from typing import List, Optional

import numpy as np
import pandas as pd


class DPDAnalyzer:
    """
    Analyzer for Days Past Due (DPD) data.
    
    This class provides methods to assign DPD buckets, detect fields in DataFrames,
    and perform analysis on loan portfolio data.
    """
    
    def __init__(self, dpd_threshold: int = 90):
        """
        Initialize the DPD Analyzer.
        
        Args:
            dpd_threshold: The threshold in days to mark an account as defaulted.
                          Default is 90 days.
        """
        self.dpd_threshold = dpd_threshold
    
    def assign_dpd_buckets(self, dpd_df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign DPD buckets to a DataFrame containing days past due information.
        
        This method categorizes days past due into standard buckets and adds
        descriptive labels and flags.
        
        Args:
            dpd_df: DataFrame with a 'days_past_due' column
            
        Returns:
            DataFrame with added columns:
                - dpd_bucket: The bucket label (e.g., "Current", "1-29", "30-59")
                - dpd_bucket_value: Numeric value representing the bucket
                - dpd_bucket_description: Human-readable description
                - default_flag: Boolean flag indicating if account is in default
        """
        res = dpd_df.copy()
        d = pd.to_numeric(res["days_past_due"], errors="coerce").fillna(0)

        cond = [
            (d == 0),
            (d.between(1, 29)),
            (d.between(30, 59)),
            (d.between(60, 89)),
            (d.between(90, 119)),
            (d.between(120, 149)),
            (d.between(150, 179)),
            (d >= 180),
        ]
        labels = ["Current", "1-29", "30-59", "60-89", "90-119", "120-149", "150-179", "180+"]
        res["dpd_bucket"] = np.select(cond, labels, default="Unknown")
        res["dpd_bucket_value"] = np.select(cond, [0, 1, 30, 60, 90, 120, 150, 180], default=999)

        desc_map = {
            "Current": "No payment due",
            "1-29": "Early delinquency",
            "30-59": "Delinquent 30 days",
            "60-89": "Delinquent 60 days",
            "90-119": "Default 90 days",
            "120-149": "Default 120 days",
            "150-179": "Default 150 days",
            "180+": "Default 180+ days",
        }
        res["dpd_bucket_description"] = res["dpd_bucket"].map(desc_map).fillna("Unknown")
        res["default_flag"] = d >= self.dpd_threshold
        return res
    
    def detect_field(self, df: pd.DataFrame, patterns: List[str]) -> Optional[str]:
        """
        Detect a field in a DataFrame based on a list of patterns.
        
        This method tries three matching strategies in order:
        1. Exact match (case-insensitive)
        2. Contains match (case-insensitive)
        3. Regex match (case-insensitive)
        
        Args:
            df: DataFrame to search for matching column names
            patterns: List of patterns to match against column names
            
        Returns:
            The name of the first matching column, or None if no match found.
            When multiple columns match, returns the shortest column name.
        """
        cols = list(df.columns)
        
        # Exact match
        for p in patterns:
            for c in cols:
                if c == p or c.lower() == p.lower():
                    return c
        
        # Check for columns that contain the pattern.
        for p in patterns:
            p_low = p.lower()
            match = [c for c in cols if p_low in c.lower()]
            if match:
                # choose the shortest one to avoid false positives
                return min(match, key=len)
        
        # Use regular expression as a fallback.
        for p in patterns:
            try:
                rgx = re.compile(p, re.IGNORECASE)
                hit = [c for c in cols if rgx.search(c)]
                if hit:
                    return min(hit, key=len)
            except re.error:
                continue
        
        return None
