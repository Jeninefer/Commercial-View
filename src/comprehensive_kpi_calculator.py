"""Comprehensive KPI Calculator for portfolio metrics"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
from .config import KPIConfig


class ComprehensiveKPICalculator:
    """
    Calculator for comprehensive portfolio KPIs.
    Handles loan portfolio analysis and risk metrics.
    """

    def __init__(self, config: Optional[KPIConfig] = None):
        self.config = config or KPIConfig()
        self.logger = logging.getLogger("abaco_dashboard")

    def calculate_all_kpis(self, loan_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all portfolio KPIs from loan data.
        
        Args:
            loan_df: DataFrame containing loan portfolio data
            
        Returns:
            Dictionary containing calculated KPIs
        """
        if not isinstance(loan_df, pd.DataFrame) or loan_df.empty:
            raise ValueError("loan_df must be a non-empty DataFrame")

        kpis = {
            "total_loans": int(len(loan_df)),
            "portfolio_metrics": self._calculate_portfolio_metrics(loan_df),
            "risk_metrics": self._calculate_risk_metrics(loan_df),
            "performance_metrics": self._calculate_performance_metrics(loan_df),
        }

        self.logger.info(f"Calculated portfolio KPIs for {len(loan_df)} loans")
        return kpis

    def _calculate_portfolio_metrics(self, loan_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic portfolio metrics"""
        metrics = {
            "count": int(len(loan_df)),
        }
        
        # Calculate total principal if available
        if "principal" in loan_df.columns:
            metrics["total_principal"] = float(loan_df["principal"].sum())
            metrics["average_principal"] = float(loan_df["principal"].mean())
        
        # Calculate total balance if available
        if "balance" in loan_df.columns:
            metrics["total_balance"] = float(loan_df["balance"].sum())
            metrics["average_balance"] = float(loan_df["balance"].mean())
        
        return metrics

    def _calculate_risk_metrics(self, loan_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate risk-related metrics"""
        metrics = {}
        
        # Default rate calculation if status column exists
        if "status" in loan_df.columns:
            total = len(loan_df)
            defaulted = len(loan_df[loan_df["status"].isin(["default", "defaulted", "charged_off"])])
            metrics["default_rate"] = float(defaulted / total) if total > 0 else 0.0
            metrics["default_count"] = int(defaulted)
        
        # LTV (Loan-to-Value) ratio if available
        if "loan_amount" in loan_df.columns and "collateral_value" in loan_df.columns:
            loan_df_copy = loan_df[loan_df["collateral_value"] > 0].copy()
            if not loan_df_copy.empty:
                loan_df_copy["ltv"] = loan_df_copy["loan_amount"] / loan_df_copy["collateral_value"]
                metrics["average_ltv"] = float(loan_df_copy["ltv"].mean())
                metrics["max_ltv"] = float(loan_df_copy["ltv"].max())
        
        return metrics

    def _calculate_performance_metrics(self, loan_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics"""
        metrics = {}
        
        # Interest income if available
        if "interest_paid" in loan_df.columns:
            metrics["total_interest_income"] = float(loan_df["interest_paid"].sum())
        
        # Delinquency rate
        if "days_past_due" in loan_df.columns:
            total = len(loan_df)
            delinquent = len(loan_df[loan_df["days_past_due"] > 30])
            metrics["delinquency_rate"] = float(delinquent / total) if total > 0 else 0.0
            metrics["delinquent_count"] = int(delinquent)
        
        return metrics
