"""
Loan Analytics Module for Commercial View
Advanced loan analysis and metrics calculation
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Constants to avoid duplicated literals
DISBURSEMENT_AMOUNT_FIELD = 'Disbursement Amount'
DAYS_IN_DEFAULT_FIELD = 'Days in Default'
OUTSTANDING_LOAN_VALUE_FIELD = 'Outstanding Loan Value'
INTEREST_RATE_APR_FIELD = 'Interest Rate APR'
CUSTOMER_ID_FIELD = 'Customer ID'
LOAN_STATUS_FIELD = 'Loan Status'
PRODUCT_TYPE_FIELD = 'Product Type'

class LoanAnalyzer:
    """Advanced loan analysis and metrics class"""
    
    def __init__(self):
        self.logger = logger
        # Add alias_map attribute that was referenced in the code
        self.alias_map = {
            'loan_amount': DISBURSEMENT_AMOUNT_FIELD,
            'customer_id': CUSTOMER_ID_FIELD,
            'status': LOAN_STATUS_FIELD
        }
    
    def analyze_loan_portfolio(self, loan_df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive loan portfolio analysis"""
        try:
            analysis = {
                "portfolio_summary": self._get_portfolio_summary(loan_df),
                "risk_metrics": self._calculate_risk_metrics(loan_df),
                "performance_metrics": self._calculate_performance_metrics(loan_df),
                "segmentation": self._segment_portfolio(loan_df)
            }
            
            self.logger.info("Loan portfolio analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in loan portfolio analysis: {e}")
            return {"error": str(e)}
    
    def _get_portfolio_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic portfolio summary statistics"""
        summary = {
            "total_loans": len(df),
            "total_principal": df.get(DISBURSEMENT_AMOUNT_FIELD, pd.Series(dtype=float)).sum() if DISBURSEMENT_AMOUNT_FIELD in df.columns else 0,
            "average_loan_size": df.get(DISBURSEMENT_AMOUNT_FIELD, pd.Series(dtype=float)).mean() if DISBURSEMENT_AMOUNT_FIELD in df.columns else 0,
            "unique_customers": df.get(CUSTOMER_ID_FIELD, pd.Series(dtype=object)).nunique() if CUSTOMER_ID_FIELD in df.columns else 0
        }
        return summary
    
    def _calculate_risk_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate risk-related metrics"""
        risk_metrics = {}
        
        if DAYS_IN_DEFAULT_FIELD in df.columns:
            risk_metrics['default_rate'] = (df[DAYS_IN_DEFAULT_FIELD] > 0).mean()
            risk_metrics['avg_days_in_default'] = df[DAYS_IN_DEFAULT_FIELD].mean()
        
        if LOAN_STATUS_FIELD in df.columns:
            risk_metrics['status_distribution'] = df[LOAN_STATUS_FIELD].value_counts().to_dict()
        
        return risk_metrics
    
    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics"""
        performance = {}
        
        if OUTSTANDING_LOAN_VALUE_FIELD in df.columns:
            performance['total_outstanding'] = df[OUTSTANDING_LOAN_VALUE_FIELD].sum()
            performance['avg_outstanding'] = df[OUTSTANDING_LOAN_VALUE_FIELD].mean()
        
        if INTEREST_RATE_APR_FIELD in df.columns:
            performance['avg_interest_rate'] = df[INTEREST_RATE_APR_FIELD].mean()
            performance['interest_rate_range'] = {
                'min': df[INTEREST_RATE_APR_FIELD].min(),
                'max': df[INTEREST_RATE_APR_FIELD].max()
            }
        
        return performance
    
    def _segment_portfolio(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Segment portfolio by various criteria"""
        segments = {}
        
        # Segment by product type
        if PRODUCT_TYPE_FIELD in df.columns:
            segments['by_product_type'] = df[PRODUCT_TYPE_FIELD].value_counts().to_dict()
        
        # Segment by loan size
        if DISBURSEMENT_AMOUNT_FIELD in df.columns:
            df_temp = df.copy()
            df_temp['loan_size_segment'] = pd.cut(
                df_temp[DISBURSEMENT_AMOUNT_FIELD], 
                bins=3, 
                labels=['Small', 'Medium', 'Large']
            )
            segments['by_loan_size'] = df_temp['loan_size_segment'].value_counts().to_dict()
        
        return segments

# Alias for backwards compatibility
class LoanAnalytics(LoanAnalyzer):
    """Alias for LoanAnalyzer"""
    pass


if __name__ == "__main__":
    # Test the module independently
    print("LoanAnalytics module loaded successfully")
    analytics = LoanAnalyzer()
    print(f"Available metrics: {list(analytics.alias_map.keys())}")
