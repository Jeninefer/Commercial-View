"""
Payment processor module extracted from PRs #20-25
Loan payment analysis and DPD calculation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any


class PaymentProcessor:
    """Payment processing for loan payment analysis and DPD calculation"""

    def __init__(self):
        self.payment_fields = ["payment_amount", "payment_date", "scheduled_date"]

    def calculate_dpd_from_payments(self, payment_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate days past due from payment schedule vs actual payments"""
        result_df = payment_df.copy()

        if (
            "scheduled_date" in result_df.columns
            and "payment_date" in result_df.columns
        ):
            result_df["scheduled_date"] = pd.to_datetime(result_df["scheduled_date"])
            result_df["payment_date"] = pd.to_datetime(result_df["payment_date"])
            result_df["days_past_due"] = (
                result_df["payment_date"] - result_df["scheduled_date"]
            ).dt.days
            result_df["days_past_due"] = result_df["days_past_due"].clip(lower=0)

        return result_df

    def analyze_payment_patterns(self, payment_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze payment patterns and performance metrics"""
        analysis = {
            "on_time_payments": 0,
            "late_payments": 0,
            "avg_payment_delay": 0.0,
            "payment_frequency": {},
        }

        if "days_past_due" in payment_df.columns:
            on_time = payment_df["days_past_due"] <= 0
            analysis["on_time_payments"] = int(on_time.sum())
            analysis["late_payments"] = int((~on_time).sum())
            analysis["avg_payment_delay"] = float(payment_df["days_past_due"].mean())

        return analysis

    def eliminate_redundant_standardization(
        self, payment_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Refactored payment analysis to eliminate redundant data standardization from PRs #31-40"""
        # Remove duplicate standardization logic
        if hasattr(self, "_standardized_cache"):
            return self._standardized_cache

        standardized_df = payment_data.copy()
        # Apply standardization only once
        self._standardized_cache = standardized_df

        return standardized_df
