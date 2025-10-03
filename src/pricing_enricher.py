"""
Pricing Enricher Module

This module provides functionality to discover, load, and enrich loan data with pricing information
from various file formats (CSV, Parquet, JSON, YAML).
"""

import os
import logging
from typing import Dict, Optional, Tuple, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def _load_any(path: str) -> pd.DataFrame:
    """Load pricing data from various file formats.
    
    Args:
        path: Path to the pricing file
        
    Returns:
        DataFrame containing the pricing data
        
    Raises:
        ValueError: If file type is not supported
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in (".parquet", ".pq"):
        return pd.read_parquet(path)
    if ext == ".json":
        return pd.read_json(path)
    if ext in (".yml", ".yaml"):
        import yaml
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        # Handle both dict and list formats
        if isinstance(cfg, dict):
            payload = cfg.get("pricing_grid", cfg.get("recommended_pricing", cfg))
        else:
            payload = cfg
        return pd.DataFrame(payload)
    raise ValueError(f"Unsupported file type: {ext}")


class PricingEnricher:
    """Class to handle pricing data discovery, loading, and loan enrichment."""
    
    DEFAULT_PRICING_PATHS = ["./data/pricing", "./pricing", "./data"]
    
    def __init__(self, pricing_paths: Optional[List[str]] = None):
        """Initialize the PricingEnricher.
        
        Args:
            pricing_paths: List of paths to search for pricing files.
                          If None, uses DEFAULT_PRICING_PATHS.
        """
        self.pricing_paths = pricing_paths or self.DEFAULT_PRICING_PATHS
        self.pricing_grid: Optional[pd.DataFrame] = None
        self.recommended_pricing: Optional[pd.DataFrame] = None
    
    def find_pricing_files(self) -> Dict[str, str]:
        """Return {'pricing_grid': path?, 'recommended_pricing': path?} with stable priority.
        
        Searches configured pricing paths for pricing files and classifies them based on
        filename patterns. Prioritizes files based on their type and order of discovery.
        
        Returns:
            Dictionary mapping pricing types to file paths
        """
        exts = (".csv", ".parquet", ".pq", ".json", ".yml", ".yaml")
        ranks = {"recommended_pricing": 0, "pricing_grid": 1}
        best: Dict[str, Tuple[int, str]] = {}

        for base in self.pricing_paths:
            if not os.path.isdir(base):
                logger.debug(f"Pricing path not found: {base}")
                continue
            for fn in os.listdir(base):
                if not fn.lower().endswith(exts):
                    continue
                lower = fn.lower()
                fpath = os.path.join(base, fn)
                # classify
                if any(k in lower for k in ["recommend", "matrix"]):
                    kind = "recommended_pricing"
                elif "grid" in lower or "price" in lower:
                    kind = "pricing_grid"
                else:
                    continue
                rank = ranks[kind]
                # prefer earlier in DEFAULT_PRICING_PATHS order, then filename order
                if kind not in best or rank <= best[kind][0]:
                    best[kind] = (rank, fpath)

        out = {k: v for k, (_, v) in best.items()}
        if not out:
            logger.warning("No pricing files discovered in configured paths")
        else:
            for k, p in out.items():
                logger.info(f"Discovered {k}: {p}")
        return out
    
    def load_pricing_data(self, pricing_files: Optional[Dict[str, str]] = None) -> bool:
        """Load pricing data from files.
        
        Args:
            pricing_files: Dictionary mapping pricing types to file paths.
                          If None, uses find_pricing_files() to discover files.
        
        Returns:
            True if at least one pricing dataset was loaded successfully, False otherwise
        """
        files = pricing_files or self.find_pricing_files()
        if not files:
            return False
        try:
            if "pricing_grid" in files:
                self.pricing_grid = _load_any(files["pricing_grid"])
                logger.info(f"Loaded pricing_grid {self.pricing_grid.shape}")
            if "recommended_pricing" in files:
                self.recommended_pricing = _load_any(files["recommended_pricing"])
                logger.info(f"Loaded recommended_pricing {self.recommended_pricing.shape}")
        except Exception as e:
            logger.error(f"Pricing load error: {e}")
        return (isinstance(self.pricing_grid, pd.DataFrame) and not self.pricing_grid.empty) or \
               (isinstance(self.recommended_pricing, pd.DataFrame) and not self.recommended_pricing.empty)
    
    def detect_join_keys(self, df: pd.DataFrame, pricing_df: pd.DataFrame) -> Tuple[list, list]:
        """Automatically detect join keys between loan and pricing dataframes.
        
        Args:
            df: Loan dataframe
            pricing_df: Pricing dataframe
            
        Returns:
            Tuple of (loan_keys, pricing_keys) where keys at same index correspond
        """
        candidates = [
            ("country", "country"), ("sector", "sector"), ("risk_band", "risk_band"),
            ("client_segment", "segment"), ("customer_segment", "segment"), ("segment", "segment"),
            ("tenor_days", "tenor_days"), ("term", "term"),
            ("ticket_usd", "ticket_usd"), ("loan_amount", "amount"), ("amount", "amount")
        ]
        lk, pk = [], []
        for l, p in candidates:
            if l in df.columns:
                pcol = p if p in pricing_df.columns else next((c for c in pricing_df.columns if c.lower() == p.lower()), None)
                if pcol:
                    lk.append(l)
                    pk.append(pcol)
        if not lk:
            logger.warning("No deterministic join keys found")
        return lk, pk
    
    def enrich_loan_data(
        self,
        loan_df: pd.DataFrame,
        *,
        join_keys: Optional[list] = None,
        band_keys: Optional[Dict[str, Tuple[str, str]]] = None,  # e.g. {"tenor_days": ("tenor_min","tenor_max")}
        apr_col_hint: Optional[str] = None,
        eir_col_hint: Optional[str] = None,
        recommended_rate_col: str = "recommended_rate"
    ) -> pd.DataFrame:
        """Enrich loan data with pricing information.
        
        This method performs a multi-stage enrichment:
        1. Exact joins with recommended_pricing
        2. Exact joins with pricing_grid for rows missing recommended rates
        3. Band-based matching for pricing_grid
        4. Calculate APR-EIR spread if columns are available
        5. Add has_pricing flag
        
        Args:
            loan_df: Loan dataframe to enrich
            join_keys: List of column names to use for joining (optional)
            band_keys: Dictionary mapping feature columns to (min, max) column names in pricing grid
            apr_col_hint: Hint for APR column name
            eir_col_hint: Hint for EIR column name
            recommended_rate_col: Column name for recommended rate
            
        Returns:
            Enriched loan dataframe
        """
        result = loan_df.copy()
        
        # Calculate APR–EIR spread first (independent of pricing data)
        apr_candidates = [apr_col_hint] if apr_col_hint else [c for c in result.columns if "apr" in c.lower()]
        eir_candidates = [eir_col_hint] if eir_col_hint else [c for c in result.columns if "eir" in c.lower()]
        apr = next((c for c in apr_candidates if c and c in result.columns), None)
        eir = next((c for c in eir_candidates if c and c in result.columns), None)
        if apr and eir:
            result["apr_eir_spread"] = pd.to_numeric(result[apr], errors="coerce") - pd.to_numeric(result[eir], errors="coerce")
            extreme = result["apr_eir_spread"].abs() > 0.5  # 50pp guard
            if extreme.any():
                logger.warning(f"Extreme APR–EIR spread on {int(extreme.sum())} rows")
        
        if ((self.pricing_grid is None or getattr(self.pricing_grid, "empty", False)) and
            (self.recommended_pricing is None or getattr(self.recommended_pricing, "empty", False))):
            if not self.load_pricing_data():
                logger.warning("No pricing data available for enrichment")
                # Add has_pricing flag even when no pricing data
                result["has_pricing"] = False
                return result

        def _apply_exact(pricing_df: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
            """Apply exact join between base and pricing dataframes."""
            if pricing_df is None or pricing_df.empty:
                return base
            keys_l, keys_p = (join_keys, join_keys) if join_keys else self.detect_join_keys(base, pricing_df)
            if not keys_l:
                return base
            p = pricing_df.copy()
            for l, pkey in zip(keys_l, keys_p):
                if pkey != l:
                    p.rename(columns={pkey: l}, inplace=True)
            merged = base.merge(p, on=keys_l, how="left", suffixes=("", "_pricing"))
            # count matches by any new col not present originally
            new_cols = [c for c in merged.columns if c not in base.columns]
            matched = merged[new_cols].notna().any(axis=1).sum() if new_cols else 0
            logger.info(f"Exact-joined {matched} / {len(merged)} rows on {keys_l}")
            return merged

        def _apply_bands(pricing_df: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
            """Apply band-based matching between base and pricing dataframes."""
            if not band_keys or pricing_df is None or pricing_df.empty:
                return base
            out = base.copy()
            grid = pricing_df.copy()

            for feat, (lo_col, hi_col) in band_keys.items():
                if feat not in out.columns or lo_col not in grid.columns or hi_col not in grid.columns:
                    raise ValueError(f"Band mapping requires {feat} in loans and {lo_col}/{hi_col} in pricing grid")
                vals = pd.to_numeric(out[feat], errors="coerce")
                lo = pd.to_numeric(grid[lo_col], errors="coerce").fillna(-np.inf)
                hi = pd.to_numeric(grid[hi_col], errors="coerce").fillna(np.inf)

                # choose first matching band per row
                sel_idx = pd.Series(-1, index=out.index, dtype=int)
                for i, (a, b) in enumerate(zip(lo, hi)):
                    mask = sel_idx.eq(-1) & vals.ge(a) & vals.le(b)
                    sel_idx[mask] = i

                matched = grid.iloc[sel_idx.clip(lower=0)].reset_index(drop=True)
                add_cols = [c for c in matched.columns if c not in out.columns]
                out = pd.concat([out.reset_index(drop=True), matched[add_cols]], axis=1)

            logger.info("Band pricing applied")
            return out

        # 1) recommended_pricing first
        if isinstance(self.recommended_pricing, pd.DataFrame) and not self.recommended_pricing.empty:
            result = _apply_exact(self.recommended_pricing, result)

        # 2) grid on rows still missing recommended_rate
        if isinstance(self.pricing_grid, pd.DataFrame) and not self.pricing_grid.empty:
            if recommended_rate_col in result.columns:
                needs_mask = result[recommended_rate_col].isna()
                if needs_mask.any():
                    needs_grid = result.loc[needs_mask].copy()
                    tmp = _apply_exact(self.pricing_grid, needs_grid)
                    if band_keys:
                        tmp = _apply_bands(self.pricing_grid, tmp)
                    # Handle column conflicts - merge may have created _pricing suffixed columns
                    for col in tmp.columns:
                        if col.endswith("_pricing"):
                            base_col = col[:-8]  # Remove "_pricing" suffix
                            if base_col in result.columns:
                                # Fill NaN values in the base column with values from the suffixed column
                                # Use .values to handle index mismatch (merge resets indices)
                                current_values = result.loc[needs_mask, base_col].values
                                tmp_values = tmp[col].values
                                filled = np.where(pd.isna(current_values), tmp_values, current_values)
                                result.loc[needs_mask, base_col] = filled
                        elif col not in result.columns and col not in loan_df.columns:
                            # New column from pricing grid, add it
                            result.loc[needs_mask, col] = tmp[col].values
            else:
                # No recommended_rate column yet, apply grid to all
                result = _apply_exact(self.pricing_grid, result)
                if band_keys:
                    result = _apply_bands(self.pricing_grid, result)

        # has_pricing flag
        result["has_pricing"] = result.get(recommended_rate_col, pd.Series(False, index=result.index)).notna()

        return result
