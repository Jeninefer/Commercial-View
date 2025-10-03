"""
KPI Module

Handles startup, fintech, valuation metrics, viability index calculation, and export.
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class StartupMetrics:
    """Calculate startup-related KPIs."""
    
    @staticmethod
    def calculate_burn_rate(expenses: float, period_months: int = 1) -> float:
        """
        Calculate monthly burn rate.
        
        Args:
            expenses: Total expenses
            period_months: Period in months
        
        Returns:
            float: Monthly burn rate
        """
        if period_months <= 0:
            return 0.0
        return expenses / period_months
    
    @staticmethod
    def calculate_runway(cash_balance: float, monthly_burn_rate: float) -> float:
        """
        Calculate runway in months.
        
        Args:
            cash_balance: Current cash balance
            monthly_burn_rate: Monthly burn rate
        
        Returns:
            float: Runway in months
        """
        if monthly_burn_rate <= 0:
            return float('inf')
        return cash_balance / monthly_burn_rate
    
    @staticmethod
    def calculate_ltv_cac_ratio(customer_lifetime_value: float, 
                               customer_acquisition_cost: float) -> float:
        """
        Calculate LTV:CAC ratio.
        
        Args:
            customer_lifetime_value: Lifetime value of customer
            customer_acquisition_cost: Cost to acquire customer
        
        Returns:
            float: LTV:CAC ratio
        """
        if customer_acquisition_cost <= 0:
            return 0.0
        return customer_lifetime_value / customer_acquisition_cost


class FintechMetrics:
    """Calculate fintech-specific KPIs."""
    
    @staticmethod
    def calculate_npl_ratio(non_performing_loans: float, total_loans: float) -> float:
        """
        Calculate Non-Performing Loan (NPL) ratio.
        
        Args:
            non_performing_loans: Amount of non-performing loans
            total_loans: Total loan portfolio amount
        
        Returns:
            float: NPL ratio as decimal
        """
        if total_loans <= 0:
            return 0.0
        return non_performing_loans / total_loans
    
    @staticmethod
    def calculate_portfolio_yield(interest_income: float, average_portfolio: float,
                                 period_months: int = 12) -> float:
        """
        Calculate annualized portfolio yield.
        
        Args:
            interest_income: Interest income earned
            average_portfolio: Average portfolio size
            period_months: Period in months
        
        Returns:
            float: Annualized yield as decimal
        """
        if average_portfolio <= 0 or period_months <= 0:
            return 0.0
        
        return (interest_income / average_portfolio) * (12 / period_months)
    
    @staticmethod
    def calculate_default_rate(defaults: float, total_loans: float) -> float:
        """
        Calculate default rate.
        
        Args:
            defaults: Number or amount of defaults
            total_loans: Total number or amount of loans
        
        Returns:
            float: Default rate as decimal
        """
        if total_loans <= 0:
            return 0.0
        return defaults / total_loans
    
    @staticmethod
    def calculate_loss_given_default(recovery_amount: float, 
                                    exposure_at_default: float) -> float:
        """
        Calculate Loss Given Default (LGD).
        
        Args:
            recovery_amount: Amount recovered
            exposure_at_default: Total exposure at default
        
        Returns:
            float: LGD as decimal
        """
        if exposure_at_default <= 0:
            return 0.0
        return 1 - (recovery_amount / exposure_at_default)


class ValuationMetrics:
    """Calculate valuation-related metrics."""
    
    @staticmethod
    def calculate_revenue_multiple(valuation: float, annual_revenue: float) -> float:
        """
        Calculate revenue multiple.
        
        Args:
            valuation: Company valuation
            annual_revenue: Annual revenue
        
        Returns:
            float: Revenue multiple
        """
        if annual_revenue <= 0:
            return 0.0
        return valuation / annual_revenue
    
    @staticmethod
    def calculate_ebitda_multiple(valuation: float, ebitda: float) -> float:
        """
        Calculate EBITDA multiple.
        
        Args:
            valuation: Company valuation
            ebitda: EBITDA
        
        Returns:
            float: EBITDA multiple
        """
        if ebitda <= 0:
            return 0.0
        return valuation / ebitda
    
    @staticmethod
    def calculate_book_value_multiple(market_value: float, book_value: float) -> float:
        """
        Calculate book value multiple (P/B ratio).
        
        Args:
            market_value: Market value
            book_value: Book value
        
        Returns:
            float: Book value multiple
        """
        if book_value <= 0:
            return 0.0
        return market_value / book_value


class ViabilityIndex:
    """Calculate composite viability index."""
    
    DEFAULT_WEIGHTS = {
        'profitability': 0.25,
        'liquidity': 0.20,
        'growth': 0.20,
        'efficiency': 0.15,
        'risk': 0.20
    }
    
    @classmethod
    def calculate_viability_index(cls, metrics: Dict[str, float],
                                  weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate composite viability index.
        
        Args:
            metrics: Dictionary of normalized metrics (0-100 scale)
            weights: Optional custom weights (must sum to 1.0)
        
        Returns:
            float: Viability index (0-100)
        """
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS
        
        # Validate weights
        if abs(sum(weights.values()) - 1.0) > 0.01:
            logger.warning("Weights do not sum to 1.0, normalizing")
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
        
        # Calculate weighted score
        score = 0.0
        for metric, value in metrics.items():
            weight = weights.get(metric, 0.0)
            # Ensure value is normalized (0-100)
            normalized_value = max(0, min(100, value))
            score += normalized_value * weight
        
        logger.debug(f"Calculated viability index: {score:.2f}")
        return score
    
    @classmethod
    def calculate_category_score(cls, category_metrics: Dict[str, float]) -> float:
        """
        Calculate score for a category of metrics.
        
        Args:
            category_metrics: Dictionary of metrics in category
        
        Returns:
            float: Category score (0-100)
        """
        if not category_metrics:
            return 0.0
        
        return sum(category_metrics.values()) / len(category_metrics)


class KPIExporter:
    """Export KPI data to various formats."""
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame, file_path: str) -> bool:
        """
        Export KPIs to CSV.
        
        Args:
            df: DataFrame with KPI data
            file_path: Output file path
        
        Returns:
            bool: Success status
        """
        try:
            df.to_csv(file_path, index=False)
            logger.info(f"Exported KPIs to CSV: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame, file_path: str, 
                       sheet_name: str = 'KPIs') -> bool:
        """
        Export KPIs to Excel.
        
        Args:
            df: DataFrame with KPI data
            file_path: Output file path
            sheet_name: Sheet name
        
        Returns:
            bool: Success status
        """
        try:
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
            logger.info(f"Exported KPIs to Excel: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], file_path: str, 
                      indent: int = 2) -> bool:
        """
        Export KPIs to JSON.
        
        Args:
            data: Dictionary with KPI data
            file_path: Output file path
            indent: JSON indent level
        
        Returns:
            bool: Success status
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)
            logger.info(f"Exported KPIs to JSON: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False


def calculate_all_kpis(df: pd.DataFrame, kpi_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculate all configured KPIs.
    
    Args:
        df: Input dataframe
        kpi_config: Configuration for KPIs to calculate
    
    Returns:
        pd.DataFrame: DataFrame with calculated KPIs
    """
    result = df.copy()
    
    # Calculate startup metrics if configured
    if kpi_config.get('startup_metrics'):
        if 'expenses' in result.columns and 'period_months' in result.columns:
            result['burn_rate'] = result.apply(
                lambda row: StartupMetrics.calculate_burn_rate(
                    row['expenses'], row.get('period_months', 1)
                ), axis=1
            )
    
    # Calculate fintech metrics if configured
    if kpi_config.get('fintech_metrics'):
        if 'non_performing_loans' in result.columns and 'total_loans' in result.columns:
            result['npl_ratio'] = result.apply(
                lambda row: FintechMetrics.calculate_npl_ratio(
                    row['non_performing_loans'], row['total_loans']
                ), axis=1
            )
    
    # Calculate valuation metrics if configured
    if kpi_config.get('valuation_metrics'):
        if 'valuation' in result.columns and 'annual_revenue' in result.columns:
            result['revenue_multiple'] = result.apply(
                lambda row: ValuationMetrics.calculate_revenue_multiple(
                    row['valuation'], row['annual_revenue']
                ), axis=1
            )
    
    logger.info(f"Calculated KPIs for {len(result)} records")
    return result


def export_kpis(data: Any, file_path: str, format: str = 'csv') -> bool:
    """
    Export KPIs to file.
    
    Args:
        data: KPI data (DataFrame or dict)
        file_path: Output file path
        format: Export format ('csv', 'excel', 'json')
    
    Returns:
        bool: Success status
    """
    format = format.lower()
    
    if format == 'csv':
        if isinstance(data, pd.DataFrame):
            return KPIExporter.export_to_csv(data, file_path)
        else:
            logger.error("CSV export requires DataFrame")
            return False
    
    elif format == 'excel':
        if isinstance(data, pd.DataFrame):
            return KPIExporter.export_to_excel(data, file_path)
        else:
            logger.error("Excel export requires DataFrame")
            return False
    
    elif format == 'json':
        if isinstance(data, dict):
            return KPIExporter.export_to_json(data, file_path)
        elif isinstance(data, pd.DataFrame):
            return KPIExporter.export_to_json(data.to_dict('records'), file_path)
        else:
            logger.error("JSON export requires dict or DataFrame")
            return False
    
    else:
        logger.error(f"Unsupported format: {format}")
        return False
