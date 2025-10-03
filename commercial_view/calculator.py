"""
Calculator class with safe mathematical operations
"""

from typing import Union
import numpy as np
import pandas as pd


class Calculator:
    """A calculator class for safe mathematical operations."""
    
    def safe_division(self,
                      numerator: Union[float, pd.Series, np.ndarray],
                      denominator: Union[float, pd.Series, np.ndarray],
                      default: float = np.nan) -> Union[float, pd.Series, np.ndarray]:
        """
        Safely divide numerator by denominator, returning default value on division by zero.
        
        Args:
            numerator: The numerator value(s) - can be scalar, pandas Series, or numpy array
            denominator: The denominator value(s) - can be scalar, pandas Series, or numpy array
            default: The default value to return when division by zero or invalid operation occurs
            
        Returns:
            Result of division with default value replacing invalid operations
        """
        num = numerator
        den = denominator
        # Scalars
        if np.isscalar(num) and np.isscalar(den):
            return default if den in (0, None) else num / den
        # Array-like
        num = pd.Series(num) if not isinstance(num, (pd.Series, np.ndarray)) else num
        den = pd.Series(den) if not isinstance(den, (pd.Series, np.ndarray)) else den
        # Convert numpy arrays to Series for consistent handling
        was_array = isinstance(num, np.ndarray) and isinstance(den, np.ndarray)
        if isinstance(num, np.ndarray):
            num = pd.Series(num)
        if isinstance(den, np.ndarray):
            den = pd.Series(den)
        num = pd.to_numeric(num, errors="coerce")
        den = pd.to_numeric(den, errors="coerce")
        with np.errstate(divide="ignore", invalid="ignore"):
            out = num.values / den.values
        out = np.where((den.values == 0) | ~np.isfinite(out), default, out)
        return out if was_array else pd.Series(out, index=num.index)
