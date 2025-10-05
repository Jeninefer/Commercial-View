"""
Feature engineering module extracted from PR #8 and #9
Customer classification and data processing utilities
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, Optional

class FeatureEngineer:
    """Feature engineering for commercial lending analytics"""
    
    CUSTOMER_TYPES = {
        'NEW': 'New',
        'RECURRENT': 'Recurrent',
        'RECOVERED': 'Recovered'
    }
    
    def classify_client_type(self,
                           df: pd.DataFrame,
                           customer_id_col: str = 'customer_id',
                           loan_count_col: str = 'loan_count', 
                           last_active_col: str = 'last_active_date',
                           reference_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Classify as New / Recurrent / Recovered based on loan count and gaps.
        If last gap >90d and returns => Recovered; if >1 loan and gaps <=90d => Recurrent; else New.
        """
        ref = (reference_date or datetime.now()).date()
        out = df.copy()
        if last_active_col in out.columns:
            out[last_active_col] = pd.to_datetime(out[last_active_col]).dt.date
            out["days_since_last"] = (pd.to_datetime(ref) - 
                                    pd.to_datetime(out[last_active_col])).dt.days
        else:
            out["days_since_last"] = np.nan

        def _label(row: pd.Series) -> str:
            cnt = row.get(loan_count_col, 0) or 0
            dsl = row.get("days_since_last", np.nan)
            if cnt <= 1:
                return self.CUSTOMER_TYPES['NEW']
            if pd.notna(dsl) and dsl > 90:
                return self.CUSTOMER_TYPES['RECOVERED']
            return self.CUSTOMER_TYPES['RECURRENT']

        out["customer_type"] = out.apply(_label, axis=1)
        return out
    
    def calculate_weighted_stats(self, portfolio_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate weighted statistics for portfolio analysis"""
        weighted_stats = {
            'weighted_apr': 0.0,
            'weighted_tenor': 0.0,
            'weighted_amount': 0.0
        }
        
        if 'outstanding_balance' in portfolio_data.columns and 'apr' in portfolio_data.columns:
            total_balance = portfolio_data['outstanding_balance'].sum()
            if total_balance > 0:
                weighted_stats['weighted_apr'] = (
                    (portfolio_data['apr'] * portfolio_data['outstanding_balance']).sum() 
                    / total_balance
                )
        
        # ...existing code for other weighted calculations...
        
        return {}
    
    def calculate_customer_dpd_stats(self, payment_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate customer-level DPD statistics"""
        dpd_stats: Dict[str, Any] = {
            'avg_dpd': 0.0,
            'max_dpd': 0,
            'customers_in_arrears': 0,
            'dpd_distribution': {}
        }
        
        # ...existing code for DPD calculations...
        
        return dpd_stats
    
    def engineer_risk_features(self, loan_data: pd.DataFrame) -> pd.DataFrame:
        """Engineer risk-related features for analysis"""
        # ...existing code for risk feature creation...
        
        loan_data['risk_score'] = 0.0  # Placeholder
        loan_data['risk_category'] = 'low'  # Default
        return loan_data
