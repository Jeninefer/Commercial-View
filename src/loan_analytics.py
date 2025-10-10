"""
Loan analytics module extracted from PRs #10, #11
Weighted statistics calculations for commercial lending portfolios
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LoanAnalytics:
    """Analytics class for weighted portfolio calculations"""

    def __init__(self):
        self.alias_map = {
            "apr": ["apr", "effective_apr", "annual_rate", "tasa_anual"],
            "eir": ["eir", "effective_interest_rate", "tasa_efectiva"],
            "term": ["term", "tenor_days", "plazo_dias", "tenor"],
        }

    def calculate_weighted_stats(
        self,
        loan_df: pd.DataFrame,
        weight_field: str = "outstanding_balance",
        metrics: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Calculate weighted averages with alias resolution and data guards"""
        alias_map = self.alias_map
        targets = metrics or ["apr", "eir", "term"]
        df = loan_df.copy()

        # Resolve weight field or detect alternative
        if weight_field not in df.columns:
            candidates = [
                "outstanding_balance",
                "olb",
                "current_balance",
                "saldo_actual",
                "balance",
            ]
            found_weight_field = next(
                (c for c in df.columns for k in candidates if k.lower() in c.lower()),
                None,
            )
            if found_weight_field is not None:
                weight_field = found_weight_field
            else:
                logger.error("Weight field not found; cannot compute weighted stats.")
                return pd.DataFrame()

        # Map each target to the first existing column that matches its aliases
        resolved_cols: Dict[str, Optional[str]] = {}
        lc_cols = {c.lower(): c for c in df.columns}
        for tgt in targets:
            found = None
            for alias in alias_map.get(tgt, [tgt]):
                # exact lower match or substring match
                if alias.lower() in lc_cols:
                    found = lc_cols[alias.lower()]
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

            wavg = np.average(
                sub[col].astype(float), weights=sub[weight_field].astype(float)
            )
            out[f"weighted_{tgt}"] = float(wavg)
            logger.info(f"Weighted {tgt}: {wavg:.6f}")

        return pd.DataFrame([out]) if out else pd.DataFrame()


if __name__ == "__main__":
    # Test the module independently
    print("LoanAnalytics module loaded successfully")
    analytics = LoanAnalytics()
    print(f"Available metrics: {list(analytics.alias_map.keys())}")
