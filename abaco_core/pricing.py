import pandas as pd
import numpy as np
import os
from typing import Optional, Dict, Tuple, List
from pathlib import Path
import logging

logger = logging.getLogger("abaco_core.pricing")

class PricingEnricher:
    DEFAULT_PRICING_PATHS = ["./exports/public", "./abaco_runtime/exports", "./exports"]
    PRICING_FILE_PATTERNS = ["pricing_grid", "recommended_pricing", "pricing_recommendations", "price_matrix"]

    def __init__(self, pricing_paths: Optional[List[str]] = None):
        self.pricing_paths = pricing_paths or self.DEFAULT_PRICING_PATHS
        self.pricing_grid: Optional[pd.DataFrame] = None
        self.recommended_pricing: Optional[pd.DataFrame] = None

    def find_pricing_files(self) -> Dict[str, str]:
        found: Dict[str, str] = {}
        for base in self.pricing_paths:
            if not os.path.exists(base):
                continue
            for file in os.listdir(base):
                if not file.lower().endswith(".csv"):
                    continue
                lower_name = file.lower()
                if any(p in lower_name for p in self.PRICING_FILE_PATTERNS):
                    path = os.path.join(base, file)
                    if "grid" in lower_name:
                        found["pricing_grid"] = path
                    elif any(p in lower_name for p in ["recommend", "matrix"]):
                        found["recommended_pricing"] = path
        return found

    def load_pricing_data(self, pricing_files: Optional[Dict[str, str]] = None) -> bool:
        files = pricing_files or self.find_pricing_files()
        if not files:
            return False
        if "pricing_grid" in files:
            self.pricing_grid = pd.read_csv(files["pricing_grid"])
        if "recommended_pricing" in files:
            self.recommended_pricing = pd.read_csv(files["recommended_pricing"])
        return (self.pricing_grid is not None) or (self.recommended_pricing is not None)

    def _auto_join_keys(self, df: pd.DataFrame, pricing_df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        potentials = [
            ("client_segment","segment"),
            ("customer_segment","segment"),
            ("segment","segment"),
            ("risk_score","risk_score"),
            ("risk_rating","risk_rating"),
            ("score","score"),
            ("rating","rating"),
            ("term","term"),
            ("tenure","term"),
            ("plazo","term"),
            ("loan_amount","amount"),
            ("amount","amount"),
            ("monto","amount"),
        ]
        loan_keys: List[str] = []
        price_keys: List[str] = []
        for lk, pk in potentials:
            if lk in df.columns:
                pcol = next((c for c in pricing_df.columns if c.lower() == pk.lower() or pk.lower() in c.lower()), None)
                if pcol:
                    loan_keys.append(lk)
                    price_keys.append(pcol)
        return loan_keys, price_keys

    def enrich_loan_data(self,
                         loan_df: pd.DataFrame,
                         *,
                         join_keys: Optional[List[str]] = None,
                         band_keys: Optional[Dict[str, Tuple[str, str]]] = None,
                         apr_col_hint: Optional[str] = None,
                         eir_col_hint: Optional[str] = None,
                         recommended_rate_col: str = "recommended_rate",
                         autoload: bool = True) -> pd.DataFrame:
        result = loan_df.copy()
        if result.empty:
            return result
        if autoload and self.pricing_grid is None and self.recommended_pricing is None:
            self.load_pricing_data()

        # Recommended pricing exact join
        if self.recommended_pricing is not None:
            rp = self.recommended_pricing.copy()
            lk, pk = (join_keys, join_keys) if join_keys else self._auto_join_keys(result, rp)
            if lk:
                rp_ren = rp.rename(columns={pk[i]: lk[i] for i in range(len(lk))})
                result = result.merge(rp_ren, on=lk, how="left", suffixes=("", "_rec"))

        # Grid pricing fallback
        if self.pricing_grid is not None:
            grid = self.pricing_grid.copy()
            lk, pk = (join_keys, join_keys) if join_keys else self._auto_join_keys(result, grid)
            # Interval joins if band_keys provided
            if band_keys:
                # For interval matching, do row-wise apply for the subset without recommendation
                without = result.copy()
                if recommended_rate_col in without.columns:
                    without = without[without[recommended_rate_col].isna()].copy()
                for feat, (low_col, high_col) in band_keys.items():
                    if feat in without.columns and low_col in grid.columns and high_col in grid.columns:
                        # Select rows where value falls into [low, high]
                        val = pd.to_numeric(without[feat], errors="coerce")
                        grid_low_numeric = pd.to_numeric(grid[low_col], errors="coerce")
                        grid_high_numeric = pd.to_numeric(grid[high_col], errors="coerce")
                        def pick_row(v):
                            if pd.isna(v):
                                return None
                            hits = grid[(grid_low_numeric <= v) & (grid_high_numeric >= v)]
                            return hits.iloc[0].to_dict() if not hits.empty else None
                        matched = val.apply(pick_row)
                        # Find the set of columns from the first non-None dict, if any
                        first_non_none = next((x for x in matched if x is not None), None)
                        if first_non_none is not None:
                            columns = list(first_non_none.keys())
                        else:
                            columns = []
                        # Build DataFrame with correct columns and length
                        matched_df = pd.DataFrame(
                            [{k: d.get(k, np.nan) if d is not None else np.nan for k in columns} for d in matched],
                            columns=columns
                        ).add_suffix("_grid")
                        # Validate matched_df before concatenation
                        if matched_df.empty or matched_df.isna().all().all():
                            # Create a DataFrame of the same length as 'without' with NaNs
                            expected_grid_cols = [f"{col}_grid" for col in grid.columns]
                            matched_df = pd.DataFrame(np.nan, index=without.index, columns=expected_grid_cols)
                        elif len(matched_df) != len(without):
                            logger.error(f"matched_df and without have different lengths for feature {feat}; aborting enrichment to avoid partial results.")
                            raise ValueError(f"Length mismatch between matched_df ({len(matched_df)}) and without ({len(without)}) for feature '{feat}'. Aborting enrichment.")
                        without = pd.concat([without.reset_index(drop=True), matched_df.reset_index(drop=True)], axis=1)
                if recommended_rate_col in result.columns:
                    result.update(without)
                else:
                    result = without

            else:
                if lk:
                    grid_ren = grid.rename(columns={pk[i]: lk[i] for i in range(len(lk))})
                    result = result.merge(grid_ren, on=lk, how="left", suffixes=("", "_grid"))

        # APR-EIR spread
        if apr_col_hint is not None and apr_col_hint not in result.columns:
            logger.warning(f"APR column hint '{apr_col_hint}' not found in DataFrame columns. Falling back to auto-detection.")
            apr_col_hint_valid = False
        else:
            apr_col_hint_valid = apr_col_hint is not None
        if eir_col_hint is not None and eir_col_hint not in result.columns:
            logger.warning(f"EIR column hint '{eir_col_hint}' not found in DataFrame columns. Falling back to auto-detection.")
            eir_col_hint_valid = False
        else:
            eir_col_hint_valid = eir_col_hint is not None
        apr_cols = [apr_col_hint] if apr_col_hint_valid else [c for c in result.columns if "apr" in c.lower()]
        eir_cols = [eir_col_hint] if eir_col_hint_valid else [c for c in result.columns if "eir" in c.lower()]
        apr_col = next((c for c in apr_cols if c in result.columns), None)
        eir_col = next((c for c in eir_cols if c in result.columns), None)
        if apr_col and eir_col:
            result["apr_eir_spread"] = pd.to_numeric(result[apr_col], errors="coerce") - pd.to_numeric(result[eir_col], errors="coerce")
        return result
