"""
Fintech Metrics Module

This module provides a class for computing various fintech metrics including:
- GMV (Gross Merchandise Value)
- Default Rate
- Take Rate
- EIR (Effective Interest Rate)
- APR-EIR Spread
- Active Users and Active Rate
"""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd

# Configure logger
logger = logging.getLogger(__name__)


class FintechMetricsCalculator:
    """
    A calculator for computing fintech metrics from loan, payment, and user data.
    """

    def safe_division(self, numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Perform safe division, returning a default value when division is not possible.

        Args:
            numerator: The numerator in the division
            denominator: The denominator in the division
            default: The default value to return if division is not possible

        Returns:
            The result of the division or the default value
        """
        if pd.isna(denominator) or denominator == 0:
            return default
        return numerator / denominator

    def compute_fintech_metrics(self,
                                loan_df: pd.DataFrame,
                                payment_df: Optional[pd.DataFrame] = None,
                                user_df: Optional[pd.DataFrame] = None,
                                *,
                                default_dpd_threshold: int = 180) -> Dict[str, float]:
        """
        Compute various fintech metrics from loan, payment, and user dataframes.

        Args:
            loan_df: DataFrame containing loan information
            payment_df: Optional DataFrame containing payment information
            user_df: Optional DataFrame containing user information
            default_dpd_threshold: Days past due threshold for default classification (default: 180)

        Returns:
            Dictionary containing computed metrics:
            - gmv: Gross Merchandise Value
            - default_rate: Percentage of loans in default
            - take_rate: Revenue as percentage of GMV
            - avg_eir: Average Effective Interest Rate
            - avg_apr_eir_spread: Average spread between APR and EIR
            - active_users: Number of active users
            - active_rate: Percentage of active users
        """
        m: Dict[str, float] = {}
        df = loan_df.copy()

        # GMV
        amt_col = next((c for c in df.columns if c.lower() in {"loan_amount", "amount", "monto_prestamo"}), None)
        if amt_col:
            m["gmv"] = float(pd.to_numeric(df[amt_col], errors="coerce").fillna(0).sum())
        else:
            logger.warning("GMV: loan amount column not found")

        # Default rate
        dpd_col = next((c for c in df.columns if c.lower() in {"days_past_due", "dpd", "dias_atraso"}), None)
        if dpd_col:
            dpd = pd.to_numeric(df[dpd_col], errors="coerce").fillna(0)
            defaults = int((dpd >= default_dpd_threshold).sum())
            base = len(df) if len(df) > 0 else np.nan
            m["default_rate"] = float(self.safe_division(defaults, base, 0.0))
        # Take rate
        # Only calculate take rate if revenue column exists, GMV has been computed, and GMV is non-zero.
        # This ensures that take rate (revenue as a percentage of GMV) is only computed when all required data is present and avoids division by zero.
        if "revenue" in df.columns and "gmv" in m and m["gmv"] > 0:
            rev = float(pd.to_numeric(df["revenue"], errors="coerce").fillna(0).sum())
            m["take_rate"] = float(self.safe_division(rev, m["gmv"], 0.0))

        # EIR, APR–EIR spread
        apr_col = next((c for c in df.columns if "apr" in c.lower()), None)
        eir_col = next((c for c in df.columns if "eir" in c.lower()), None)
        if eir_col:
            eir_vals = pd.to_numeric(df[eir_col], errors="coerce")
            eir_mean = eir_vals.mean()
            m["avg_eir"] = float(eir_mean) if not pd.isna(eir_mean) else None
        if apr_col and eir_col:
            if "apr_eir_spread" in df.columns:
                spread_mean = pd.to_numeric(df["apr_eir_spread"], errors="coerce").mean()
                m["avg_apr_eir_spread"] = float(spread_mean) if not pd.isna(spread_mean) else None
            else:
                apr_vals = pd.to_numeric(df[apr_col], errors="coerce")
                eir_vals = pd.to_numeric(df[eir_col], errors="coerce")
                spread_mean = (apr_vals - eir_vals).mean()
                m["avg_apr_eir_spread"] = float(spread_mean) if not pd.isna(spread_mean) else None
                m["avg_apr_eir_spread"] = float((pd.to_numeric(df[apr_col], errors="coerce") -
                                                 pd.to_numeric(df[eir_col], errors="coerce")).mean())

        # Active users
        if user_df is not None and "is_active" in user_df.columns:
            active = int(pd.to_numeric(user_df["is_active"], errors="coerce").fillna(0).sum())
            total = len(user_df) if len(user_df) > 0 else np.nan
            m["active_users"] = active
            m["active_rate"] = float(self.safe_division(active, total, 0.0))
        elif payment_df is not None and {"customer_id", "date"}.issubset(payment_df.columns):
            tmp = payment_df.copy()
            tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
            cutoff = pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=30)
            m["active_users"] = int(tmp.loc[tmp["date"] >= cutoff, "customer_id"].nunique())

        return m
