"""Enhanced KPI Calculator combining portfolio and business metrics"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
from .comprehensive_kpi_calculator import ComprehensiveKPICalculator
from .kpi_calculator import KPICalculator
from .config import KPIConfig


class EnhancedKPICalculator:
    """
    Enhanced KPI calculator combining portfolio KPIs with startup/fintech/valuation metrics.
    Production-safe: no demo data, no implicit proxies.
    """

    def __init__(self, config: Optional[KPIConfig] = None):
        self.comprehensive_calculator = ComprehensiveKPICalculator(config)
        self.sfv_calculator = KPICalculator()
        self.logger = logging.getLogger("abaco_dashboard")

    def calculate_portfolio_kpis(self, loan_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate portfolio KPIs from loan data.
        
        Args:
            loan_df: DataFrame containing loan portfolio data
            
        Returns:
            Dictionary containing portfolio KPIs
            
        Raises:
            ValueError: If loan_df is not a non-empty DataFrame
        """
        if not isinstance(loan_df, pd.DataFrame) or loan_df.empty:
            raise ValueError("loan_df must be a non-empty DataFrame")
        return self.comprehensive_calculator.calculate_all_kpis(loan_df)

    def calculate_business_metrics(
        self,
        revenue_df: pd.DataFrame,
        customer_df: pd.DataFrame,
        transaction_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Calculate business metrics including startup, fintech, and valuation metrics.
        
        Args:
            revenue_df: DataFrame containing revenue data
            customer_df: DataFrame containing customer data
            transaction_df: DataFrame containing transaction data
            
        Returns:
            Dictionary containing startup, fintech, and valuation metrics
            
        Raises:
            ValueError: If any input is not a DataFrame
        """
        if not all(isinstance(x, pd.DataFrame) for x in [revenue_df, customer_df, transaction_df]):
            raise ValueError("revenue_df, customer_df, and transaction_df must be DataFrames")
        return {
            "startup_metrics": self.sfv_calculator.compute_startup_metrics(revenue_df, customer_df),
            "fintech_metrics": self.sfv_calculator.compute_fintech_metrics(transaction_df),
            "valuation_metrics": self.sfv_calculator.compute_valuation_metrics(revenue_df, customer_df, transaction_df),
        }

    def calculate_all_metrics(
        self,
        loan_df: pd.DataFrame,
        revenue_df: Optional[pd.DataFrame] = None,
        customer_df: Optional[pd.DataFrame] = None,
        transaction_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Calculate all metrics: portfolio KPIs and business metrics.
        
        Portfolio KPIs are mandatory and always calculated.
        Business metrics are only calculated if ALL three DataFrames 
        (revenue, customer, transaction) are provided and non-empty.
        
        Args:
            loan_df: DataFrame containing loan portfolio data (required)
            revenue_df: DataFrame containing revenue data (optional)
            customer_df: DataFrame containing customer data (optional)
            transaction_df: DataFrame containing transaction data (optional)
            
        Returns:
            Dictionary containing:
            - calculation_timestamp: ISO format timestamp
            - data_summary: Summary of available data
            - portfolio_kpis: Calculated portfolio KPIs
            - business_metrics: Calculated business metrics or skip status
            
        Raises:
            ValueError: If loan_df is not a non-empty DataFrame
        """
        if not isinstance(loan_df, pd.DataFrame) or loan_df.empty:
            raise ValueError("loan_df must be a non-empty DataFrame")

        out: Dict[str, Any] = {
            "calculation_timestamp": pd.Timestamp.now(tz="UTC").isoformat(),
            "data_summary": {
                "loans_count": int(len(loan_df)),
                "revenue_available": bool(revenue_df is not None and not revenue_df.empty),
                "customer_data_available": bool(customer_df is not None and not customer_df.empty),
                "transaction_data_available": bool(transaction_df is not None and not transaction_df.empty),
            },
        }

        # Portfolio KPIs are mandatory
        out["portfolio_kpis"] = self.calculate_portfolio_kpis(loan_df)

        # Business metrics only if ALL three frames are provided and non-empty
        if all([
            isinstance(revenue_df, pd.DataFrame) and not revenue_df.empty,
            isinstance(customer_df, pd.DataFrame) and not customer_df.empty,
            isinstance(transaction_df, pd.DataFrame) and not transaction_df.empty,
        ]):
            out["business_metrics"] = self.calculate_business_metrics(revenue_df, customer_df, transaction_df)
        else:
            out["business_metrics"] = {"status": "skipped", "reason": "missing or empty inputs"}

        self.logger.info(f"All metrics calculated. Loans={len(loan_df)}")
        return out
