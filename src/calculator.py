"""
Calculator module extracted from PR #30
Safe division operations for KPI calculations
"""

import pandas as pd
import numpy as np
from typing import Union


class Calculator:
    """Calculator with safe mathematical operations for KPI calculations"""

    def safe_division(
        self,
        numerator: Union[float, pd.Series, np.ndarray],
        denominator: Union[float, pd.Series, np.ndarray],
        default: float = np.nan,
    ) -> Union[float, pd.Series, np.ndarray]:
        """
        Safe division with protection against division by zero.
        Supports scalars, pandas Series, and numpy arrays.
        """
        num = numerator
        den = denominator

        # Scalars
        if np.isscalar(num) and np.isscalar(den):
            return default if den in (0, None) else num / den

        # Array-like
        num = pd.Series(num) if not isinstance(num, (pd.Series, np.ndarray)) else num
        den = pd.Series(den) if not isinstance(den, (pd.Series, np.ndarray)) else den
        num = pd.to_numeric(num, errors="coerce")
        den = pd.to_numeric(den, errors="coerce")

        with np.errstate(divide="ignore", invalid="ignore"):
            out = num.values / den.values
            out = np.where((den.values == 0) | ~np.isfinite(out), default, out)

        return pd.Series(out, index=num.index) if isinstance(num, pd.Series) else out
