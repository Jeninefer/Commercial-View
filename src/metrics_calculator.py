"""
Metrics calculator module extracted from PR #12
Principal KPI analytics with weighted metrics calculations
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Union

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Calculator for weighted metrics in commercial lending"""
    
    def calculate_weighted_metrics(self,
                                 df: pd.DataFrame,
                                 metrics: List[str],
                                 weight_col: str = "outstanding_balance") -> Dict[str, float]:
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
    
    def safe_division(self,
                     numerator: Union[float, pd.Series, np.ndarray],
                     denominator: Union[float, pd.Series, np.ndarray],
                     default: float = np.nan) -> Union[float, pd.Series, np.ndarray]:
        """Safe division with protection against division by zero"""
        num = numerator
        den = denominator
        
        # Scalars
        if np.isscalar(num) and np.isscalar(den):
            try:
                if isinstance(num, complex) or isinstance(den, complex):
                    return float(default)
                num_f = float(num)
                den_f = float(den)
                if den_f == 0 or np.isnan(den_f):
                    return float(default)
                return num_f / den_f
            except (ValueError, TypeError):
                return float(default)
        
        # Array-like - convert to pandas Series for consistent .values access
        if isinstance(num, np.ndarray):
            num = pd.Series(num)
        if isinstance(den, np.ndarray):
            den = pd.Series(den)
            
        # Ensure Series type with proper conversion
        if not isinstance(num, pd.Series):
            try:
                if np.isscalar(num):
                    num = pd.Series([num])
                else:
                    try:
                        # Handle memoryview and other special types
                        if isinstance(num, memoryview):
                            num = pd.Series(list(num.toreadonly()))
                        elif hasattr(num, '__iter__') and not isinstance(num, (str, bytes, bytearray)):
                            # Convert to list safely
                            try:
                                num_list = list(num)
                                num = pd.Series(num_list)
                            except (TypeError, ValueError):
                                num = pd.Series([num])
                        else:
                            num = pd.Series([num])
                    except Exception:
                        num = pd.Series([num])
            except Exception:
                num = pd.Series([num])
        if not isinstance(den, pd.Series):
            try:
                if np.isscalar(den):
                    den = pd.Series([den])
                elif hasattr(den, '__iter__') and not isinstance(den, (str, bytes, bytearray)):
                    try:
                        den_list = list(den)
                        den = pd.Series(den_list)
                    except (TypeError, ValueError):
                        den = pd.Series([den])
                else:
                    den = pd.Series([den])
            except Exception:
                den = pd.Series([den])
        
        num = pd.to_numeric(num, errors="coerce")
        den = pd.to_numeric(den, errors="coerce")
        
        with np.errstate(divide="ignore", invalid="ignore"):
            out = num.values / den.values
            out = np.where((den.values == 0) | ~np.isfinite(out), default, out)
        
        # Return appropriate type based on original input
        if isinstance(numerator, pd.Series):
            return pd.Series(out, index=num.index)
        elif isinstance(numerator, np.ndarray):
            return out
        else:
            return pd.Series(out, index=num.index)
