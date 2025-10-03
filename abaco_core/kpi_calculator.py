"""
KPICalculator module for computing financial viability and performance metrics.

This module provides functionality to calculate Key Performance Indicators (KPIs)
for financial products and assess viability based on various metrics.
"""

import pandas as pd
from typing import Dict, Optional, Any


class KPICalculator:
    """
    Calculates Key Performance Indicators and viability metrics.
    
    The KPICalculator computes various financial KPIs and determines
    viability based on startup metrics and other thresholds.
    """
    
    def __init__(self):
        """Initialize the KPICalculator."""
        pass
    
    def compute_viability_index(
        self,
        loan_metrics: Optional[Dict[str, float]] = None,
        startup_metrics: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Compute a viability index based on loan and startup metrics.
        
        This method currently uses startup metrics thresholds to compute viability.
        The viability score indicates the financial health and sustainability of
        the portfolio or business.
        
        Args:
            loan_metrics: Dictionary of loan-related metrics (e.g., default rate,
                         average loan size, interest rate). Currently optional as
                         the primary calculation uses startup_metrics.
            startup_metrics: Dictionary of startup/business metrics (e.g., burn_rate,
                           runway_months, revenue_growth). Required for viability
                           calculation in the current implementation.
            thresholds: Dictionary of threshold values for each metric. If not provided,
                       uses default thresholds.
        
        Returns:
            Viability index as a float between 0.0 and 1.0, where:
            - 1.0 indicates excellent viability (all metrics meet thresholds)
            - 0.0 indicates poor viability or missing required data
        
        Note:
            Current implementation requires startup_metrics to compute viability.
            If startup_metrics are empty or None, viability_index returns 0.
            
            For pure fintech operations with only loan data (no startup metrics),
            consider one of these approaches:
            1. Document that viability_index returns 0 (N/A) without startup metrics
            2. Extend this method to compute viability from loan_metrics alone
            3. Use separate methods: compute_loan_viability() and compute_startup_viability()
            
            Current behavior: If startup_metrics is None or empty, the method returns 0.0,
            which can be interpreted as "viability not applicable" rather than "not viable".
            Ensure this is documented in your application logic.
        
        Example:
            >>> calculator = KPICalculator()
            >>> startup = {'burn_rate': 50000, 'runway_months': 18, 'revenue': 80000}
            >>> viability = calculator.compute_viability_index(startup_metrics=startup)
            >>> # Returns viability score based on startup health
            
            >>> # Case without startup metrics (pure fintech with only loans)
            >>> loan_only = {'default_rate': 0.02, 'avg_interest': 0.08}
            >>> viability = calculator.compute_viability_index(loan_metrics=loan_only)
            >>> # Returns 0.0 (not applicable, not necessarily "not viable")
        """
        # If no startup metrics provided, return 0 (viability not applicable)
        if not startup_metrics:
            return 0.0
        
        # Default thresholds if not provided
        default_thresholds = {
            'min_runway_months': 12,
            'max_burn_rate': 100000,
            'min_revenue_growth': 0.1,  # 10% growth
            'min_revenue': 50000
        }
        
        if thresholds is None:
            thresholds = default_thresholds
        
        # Calculate viability score based on startup metrics
        score = 0.0
        total_checks = 0
        
        # Check runway (months of operation remaining)
        if 'runway_months' in startup_metrics:
            total_checks += 1
            if startup_metrics['runway_months'] >= thresholds.get('min_runway_months', 12):
                score += 1.0
        
        # Check burn rate (monthly cash consumption)
        if 'burn_rate' in startup_metrics:
            total_checks += 1
            if startup_metrics['burn_rate'] <= thresholds.get('max_burn_rate', 100000):
                score += 1.0
        
        # Check revenue growth
        if 'revenue_growth' in startup_metrics:
            total_checks += 1
            if startup_metrics['revenue_growth'] >= thresholds.get('min_revenue_growth', 0.1):
                score += 1.0
        
        # Check minimum revenue
        if 'revenue' in startup_metrics:
            total_checks += 1
            if startup_metrics['revenue'] >= thresholds.get('min_revenue', 50000):
                score += 1.0
        
        # Return normalized score (0.0 to 1.0)
        if total_checks == 0:
            return 0.0
        
        return score / total_checks
    
    def calculate_portfolio_kpis(self, loans_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate key portfolio KPIs from loan data.
        
        Args:
            loans_df: DataFrame containing loan portfolio data
        
        Returns:
            Dictionary of calculated KPIs including:
            - total_loans: Total number of loans
            - total_principal: Total principal amount
            - average_loan_size: Average loan amount
            - Other relevant metrics based on available columns
        """
        kpis = {
            'total_loans': len(loans_df),
        }
        
        if 'principal' in loans_df.columns:
            kpis['total_principal'] = loans_df['principal'].sum()
            kpis['average_loan_size'] = loans_df['principal'].mean()
        
        if 'interest_rate' in loans_df.columns:
            kpis['average_interest_rate'] = loans_df['interest_rate'].mean()
        
        if 'days_past_due' in loans_df.columns:
            kpis['average_dpd'] = loans_df['days_past_due'].mean()
        
        return kpis
