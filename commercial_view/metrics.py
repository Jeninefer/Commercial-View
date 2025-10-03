"""KPI metrics calculator with weighted averages."""
import logging
from typing import Dict, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate various KPI metrics for commercial analytics."""

    def calculate_weighted_metrics(
        self,
        df: pd.DataFrame,
        metrics: List[str],
        weight_col: str = "outstanding_balance"
    ) -> Dict[str, float]:
        """
        Compute weighted averages for explicit metric columns. Guards zero/NaN weights.
        """
        results: Dict[str, float] = {}
        if weight_col not in df.columns:
            logger.error(f"Weight column {weight_col} not found.")
            return results

        base = df[[weight_col] + [m for m in metrics if m in df.columns]].dropna(subset=[weight_col])
        base = base[(base[weight_col] > 0) & np.isfinite(base[weight_col])]
        if base.empty:
            logger.warning("No valid rows to compute weighted metrics.")
            return results

        for m in metrics:
            if m not in base.columns:
                logger.warning(f"Metric {m} not found. Skipping.")
                continue
            sub = base.dropna(subset=[m])
            if sub.empty or sub[weight_col].sum() == 0:
                logger.warning(f"No valid data for {m} weighted average.")
                continue
            results[f"weighted_{m}"] = float(np.average(sub[m].astype(float), weights=sub[weight_col].astype(float)))
        return results
