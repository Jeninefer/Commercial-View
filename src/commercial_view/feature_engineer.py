"""Feature Engineering for Commercial View KPI Analysis"""

from datetime import datetime
from typing import Optional
import numpy as np
import pandas as pd


class FeatureEngineer:
    """Feature engineering class for customer classification and analysis"""
    
    # Customer type constants
    CUSTOMER_TYPES = {
        'NEW': 'New',
        'RECURRENT': 'Recurrent',
        'RECOVERED': 'Recovered'
    }
    
    def classify_client_type(
        self,
        df: pd.DataFrame,
        customer_id_col: str = 'customer_id',
        loan_count_col: str = 'loan_count',
        last_active_col: str = 'last_active_date',
        reference_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Classify as New / Recurrent / Recovered based on loan count and gaps.
        If last gap >90d and returns => Recovered; if >1 loan and gaps <=90d => Recurrent; else New.
        
        Args:
            df: Input DataFrame with customer data
            customer_id_col: Column name for customer ID (default: 'customer_id')
            loan_count_col: Column name for loan count (default: 'loan_count')
            last_active_col: Column name for last active date (default: 'last_active_date')
            reference_date: Reference date for calculation (default: current date)
            
        Returns:
            DataFrame with added 'customer_type' and 'days_since_last' columns
        """
        ref = (reference_date or datetime.now()).date()
        out = df.copy()
        if last_active_col in out.columns:
            out[last_active_col] = pd.to_datetime(out[last_active_col]).dt.date
            out["days_since_last"] = (pd.to_datetime(ref) - pd.to_datetime(out[last_active_col])).dt.days
        else:
            out["days_since_last"] = np.nan

        def _label(row):
            cnt = row.get(loan_count_col, 0) or 0
            dsl = row.get("days_since_last", np.nan)
            if cnt <= 1:
                return self.CUSTOMER_TYPES['NEW']
            if pd.notna(dsl) and dsl > 90:
                return self.CUSTOMER_TYPES['RECOVERED']
            return self.CUSTOMER_TYPES['RECURRENT']

        out["customer_type"] = out.apply(_label, axis=1)
        return out
