"""
Payment processor module extracted from PRs #20-25
Loan payment analysis and DPD calculation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple


class PaymentProcessor:
    """Payment processing for loan payment analysis and DPD calculation"""

    def __init__(self):
        self.payment_fields: List[str] = [
            "payment_amount",
            "payment_date",
            "scheduled_date",
        ]
        self._standardized_cache: Optional[pd.DataFrame] = None

    def calculate_dpd_from_payments(self, payment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate days past due from payment schedule vs actual payments

        Args:
            payment_df: DataFrame with payment_date and scheduled_date columns

        Returns:
            DataFrame with additional days_past_due column

        Example:
            >>> processor = PaymentProcessor()
            >>> df = pd.DataFrame({
            ...     'scheduled_date': ['2024-01-01', '2024-02-01'],
            ...     'payment_date': ['2024-01-05', '2024-02-01']
            ... })
            >>> result = processor.calculate_dpd_from_payments(df)
            >>> result['days_past_due'].tolist()
            [4, 0]
        """
        result_df = payment_df.copy()

        if (
            "scheduled_date" in result_df.columns
            and "payment_date" in result_df.columns
        ):
            # Convert to datetime with error handling
            result_df["scheduled_date"] = pd.to_datetime(
                result_df["scheduled_date"], errors="coerce"
            )
            result_df["payment_date"] = pd.to_datetime(
                result_df["payment_date"], errors="coerce"
            )

            # Calculate days past due (only positive values count as past due)
            result_df["days_past_due"] = (
                result_df["payment_date"] - result_df["scheduled_date"]
            ).dt.days
            result_df["days_past_due"] = result_df["days_past_due"].clip(lower=0)

        return result_df

    def analyze_payment_patterns(self, payment_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze payment patterns and performance metrics

        Args:
            payment_df: DataFrame with days_past_due column

        Returns:
            Dictionary with payment performance metrics:
            - on_time_payments: Count of payments made on or before due date
            - late_payments: Count of late payments
            - avg_payment_delay: Average days of delay
            - payment_frequency: Distribution of payment timings
        """
        analysis: Dict[str, Any] = {
            "on_time_payments": 0,
            "late_payments": 0,
            "avg_payment_delay": 0.0,
            "max_delay_days": 0,
            "payment_frequency": {},
        }

        if "days_past_due" in payment_df.columns:
            on_time = payment_df["days_past_due"] <= 0
            analysis["on_time_payments"] = int(on_time.sum())
            analysis["late_payments"] = int((~on_time).sum())
            analysis["avg_payment_delay"] = float(payment_df["days_past_due"].mean())
            analysis["max_delay_days"] = int(payment_df["days_past_due"].max())

            # Payment frequency distribution
            if "payment_date" in payment_df.columns:
                payment_df["payment_month"] = pd.to_datetime(
                    payment_df["payment_date"]
                ).dt.to_period("M")
                frequency = payment_df["payment_month"].value_counts().to_dict()
                analysis["payment_frequency"] = {
                    str(k): int(v) for k, v in frequency.items()
                }

        return analysis

    def eliminate_redundant_standardization(
        self, payment_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Refactored payment analysis to eliminate redundant data standardization

        This method implements caching to avoid redundant standardization operations
        as identified in PRs #31-40.

        Args:
            payment_data: Raw payment DataFrame

        Returns:
            Standardized payment DataFrame (cached for efficiency)
        """
        # Check if we have a cached standardized version
        if self._standardized_cache is not None:
            return self._standardized_cache

        # Standardize data only once
        standardized_df = payment_data.copy()

        # Apply standardization operations
        if "payment_amount" in standardized_df.columns:
            standardized_df["payment_amount"] = pd.to_numeric(
                standardized_df["payment_amount"], errors="coerce"
            )

        # Cache the result
        self._standardized_cache = standardized_df

        return standardized_df

    def clear_cache(self) -> None:
        """Clear the standardization cache"""
        self._standardized_cache = None

    def get_payment_summary(self, payment_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive payment summary statistics

        Args:
            payment_df: Payment DataFrame

        Returns:
            Dictionary with summary statistics
        """
        summary: Dict[str, Any] = {
            "total_payments": len(payment_df),
            "total_amount": 0.0,
            "avg_payment_amount": 0.0,
            "payment_performance": {},
        }

        if "payment_amount" in payment_df.columns:
            summary["total_amount"] = float(payment_df["payment_amount"].sum())
            summary["avg_payment_amount"] = float(payment_df["payment_amount"].mean())

        # Include payment pattern analysis
        summary["payment_performance"] = self.analyze_payment_patterns(payment_df)

        return summary
