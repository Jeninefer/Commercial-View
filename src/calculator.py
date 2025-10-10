"""
Calculator module extracted from PR #30
Safe division operations for KPI calculations
"""

import pandas as pd
import numpy as np
from typing import Union, Optional


class Calculator:
    """Calculator with safe mathematical operations for KPI calculations"""

    def safe_division(
        self,
        numerator: Union[float, int, pd.Series, np.ndarray],
        denominator: Union[float, int, pd.Series, np.ndarray],
        default: float = np.nan,
    ) -> Union[float, pd.Series, np.ndarray]:
        """
        Safe division with protection against division by zero.
        Supports scalars, pandas Series, and numpy arrays.
        
        Args:
            numerator: The dividend (can be scalar or array-like)
            denominator: The divisor (can be scalar or array-like)
            default: Value to return when division by zero occurs
            
        Returns:
            Result of safe division operation
        """
        # Handle None values
        if numerator is None or denominator is None:
            return default
            
        # Scalars
        if np.isscalar(numerator) and np.isscalar(denominator):
            # Convert to float to ensure proper division
            try:
                num_val = float(numerator)
                den_val = float(denominator)
                return default if den_val == 0.0 or not np.isfinite(den_val) else num_val / den_val
            except (TypeError, ValueError):
                return default

        # Array-like
        num = pd.Series(numerator) if not isinstance(numerator, (pd.Series, np.ndarray)) else numerator
        den = pd.Series(denominator) if not isinstance(denominator, (pd.Series, np.ndarray)) else denominator
        num = pd.to_numeric(num, errors="coerce")
        den = pd.to_numeric(den, errors="coerce")

        with np.errstate(divide="ignore", invalid="ignore"):
            out = num.values / den.values
            out = np.where((den.values == 0) | ~np.isfinite(out), default, out)

        return pd.Series(out, index=num.index) if isinstance(num, pd.Series) else out
