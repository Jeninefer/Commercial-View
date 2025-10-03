"""
Commercial View - Loan Analysis Module
Principal KPI calculation and weighted statistics
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)


class LoanAnalyzer:
    """
    Analyzes loan portfolios and calculates principal KPIs including
    weighted statistics for key metrics.
    """

    def calculate_weighted_stats(
        self,
        loan_df: pd.DataFrame,
        weight_field: str = "outstanding_balance",
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate weighted averages for specified metrics using `weight_field`.
        Resolves case/alias differences and guards against zero/NaN weights.
        
        Args:
            loan_df: DataFrame containing loan data
            weight_field: Name of the column to use as weights (default: "outstanding_balance")
            metrics: List of metric names to calculate weighted averages for.
                    Default: ["apr", "eir", "term"]
        
        Returns:
            DataFrame with one row containing weighted averages for each metric,
            with column names like "weighted_apr", "weighted_eir", etc.
            Returns empty DataFrame if no valid data or weight field not found.
        """
        # Default targets and common aliases
        alias_map = {
            "apr": ["apr", "effective_apr", "annual_rate", "tasa_anual"],
            "eir": ["eir", "effective_interest_rate", "tasa_efectiva"],
            "term": ["term", "tenor_days", "plazo_dias", "tenor"]
        }
        targets = metrics or ["apr", "eir", "term"]

        df = loan_df.copy()

        # Resolve weight field or detect a safe alternative
        if weight_field not in df.columns:
            candidates = ["outstanding_balance", "olb", "current_balance", "saldo_actual", "balance"]
            weight_field = next((c for c in df.columns for k in candidates if k.lower() in c.lower()), None) or "outstanding_balance"
            if weight_field not in df.columns:
                logger.error("Weight field not found; cannot compute weighted stats.")
                return pd.DataFrame()

        # Map each target to the first existing column that matches its aliases
        resolved_cols: Dict[str, Optional[str]] = {}
        lc_cols = {c.lower(): c for c in df.columns}
        for tgt in targets:
            found = None
            for alias in alias_map.get(tgt, [tgt]):
                # exact lower match or substring match
                if alias in lc_cols:
                    found = lc_cols[alias]
                    break
                matches = [c for c in df.columns if alias.lower() in c.lower()]
                if matches:
                    found = matches[0]
                    break
            resolved_cols[tgt] = found

        # Compute weighted averages with guards
        out: Dict[str, float] = {}
        for tgt, col in resolved_cols.items():
            if not col:
                logger.warning(f"No column found for metric '{tgt}'. Skipping.")
                continue

            sub = df[[col, weight_field]].dropna()
            # Remove non-positive or NaN weights
            sub = sub[(sub[weight_field] > 0) & np.isfinite(sub[weight_field])]
            if sub.empty or sub[weight_field].sum() == 0:
                logger.warning(f"No valid data to compute weighted {tgt}.")
                continue

            wavg = np.average(sub[col].astype(float), weights=sub[weight_field].astype(float))
            out[f"weighted_{tgt}"] = float(wavg)
            logger.info(f"Weighted {tgt}: {wavg:.6f}")

        return pd.DataFrame([out]) if out else pd.DataFrame()
