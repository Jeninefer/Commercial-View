"""
Commercial View KPI Calculator Module

This module provides comprehensive KPI calculation functions for loan portfolio analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


@dataclass
class KPIConfig:
    """Configuration for KPI calculations."""
    
    # Exposure metrics config
    include_exposure_metrics: bool = True
    
    # Yield metrics config
    include_yield_metrics: bool = True
    
    # Delinquency metrics config
    include_delinquency_metrics: bool = True
    delinquency_days_threshold: int = 30
    
    # Utilization metrics config
    include_utilization_metrics: bool = True
    
    # Segment mix metrics config
    include_segment_mix_metrics: bool = True
    
    # Vintage metrics config
    include_vintage_metrics: bool = True
    
    # Additional config options
    precision: int = 2
    include_metadata: bool = True


class ComprehensiveKPICalculator:
    """Calculator for comprehensive loan portfolio KPIs."""
    
    def __init__(self, config: Optional[KPIConfig] = None):
        """
        Initialize the KPI calculator.
        
        Args:
            config: Optional KPIConfig for customizing calculations
        """
        self.config = config if config is not None else KPIConfig()
    
    def calculate_all_kpis(self, loan_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all KPIs based on configuration.
        
        Args:
            loan_df: DataFrame containing loan data
            
        Returns:
            Dictionary containing all calculated KPIs
        """
        results = {}
        
        if self.config.include_exposure_metrics:
            results['exposure_metrics'] = self.calculate_exposure_metrics(loan_df)
        
        if self.config.include_yield_metrics:
            results['yield_metrics'] = self.calculate_yield_metrics(loan_df)
        
        if self.config.include_delinquency_metrics:
            results['delinquency_metrics'] = self.calculate_delinquency_metrics(loan_df)
        
        if self.config.include_utilization_metrics:
            results['utilization_metrics'] = self.calculate_utilization_metrics(loan_df)
        
        if self.config.include_segment_mix_metrics:
            results['segment_mix_metrics'] = self.calculate_segment_mix_metrics(loan_df)
        
        if self.config.include_vintage_metrics:
            results['vintage_metrics'] = self.calculate_vintage_metrics(loan_df)
        
        if self.config.include_metadata:
            results['metadata'] = {
                'total_loans': len(loan_df),
                'calculation_timestamp': pd.Timestamp.now().isoformat()
            }
        
        return results
    
    def calculate_exposure_metrics(self, loan_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate exposure-related metrics.
        
        Args:
            loan_df: DataFrame containing loan data with columns like 'balance', 'principal', etc.
            
        Returns:
            Dictionary of exposure metrics
        """
        metrics = {}
        
        # Total exposure
        if 'balance' in loan_df.columns:
            metrics['total_balance'] = float(loan_df['balance'].sum())
            metrics['average_balance'] = float(loan_df['balance'].mean())
            metrics['median_balance'] = float(loan_df['balance'].median())
            metrics['max_balance'] = float(loan_df['balance'].max())
            metrics['min_balance'] = float(loan_df['balance'].min())
        
        # Principal exposure
        if 'principal' in loan_df.columns:
            metrics['total_principal'] = float(loan_df['principal'].sum())
            metrics['average_principal'] = float(loan_df['principal'].mean())
        
        # Outstanding exposure
        if 'outstanding_amount' in loan_df.columns:
            metrics['total_outstanding'] = float(loan_df['outstanding_amount'].sum())
        
        return metrics
    
    def calculate_yield_metrics(self, loan_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate yield-related metrics.
        
        Args:
            loan_df: DataFrame containing loan data with columns like 'interest_rate', 'interest_income', etc.
            
        Returns:
            Dictionary of yield metrics
        """
        metrics = {}
        
        # Interest rate metrics
        if 'interest_rate' in loan_df.columns:
            metrics['average_interest_rate'] = float(loan_df['interest_rate'].mean())
            metrics['weighted_average_rate'] = 0.0
            
            # Calculate weighted average if balance is available
            if 'balance' in loan_df.columns and loan_df['balance'].sum() > 0:
                metrics['weighted_average_rate'] = float(
                    (loan_df['interest_rate'] * loan_df['balance']).sum() / loan_df['balance'].sum()
                )
        
        # Interest income metrics
        if 'interest_income' in loan_df.columns:
            metrics['total_interest_income'] = float(loan_df['interest_income'].sum())
            metrics['average_interest_income'] = float(loan_df['interest_income'].mean())
        
        # Yield calculations
        if 'interest_income' in loan_df.columns and 'balance' in loan_df.columns:
            if loan_df['balance'].sum() > 0:
                metrics['portfolio_yield'] = float(
                    (loan_df['interest_income'].sum() / loan_df['balance'].sum()) * 100
                )
        
        return metrics
    
    def calculate_delinquency_metrics(self, loan_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate delinquency-related metrics.
        
        Args:
            loan_df: DataFrame containing loan data with columns like 'days_past_due', 'delinquent', etc.
            
        Returns:
            Dictionary of delinquency metrics
        """
        metrics = {}
        
        total_loans = len(loan_df)
        
        # Delinquency rate
        if 'delinquent' in loan_df.columns:
            delinquent_count = loan_df['delinquent'].sum()
            metrics['delinquency_rate'] = float(delinquent_count / total_loans * 100) if total_loans > 0 else 0.0
            metrics['delinquent_count'] = int(delinquent_count)
            metrics['current_count'] = int(total_loans - delinquent_count)
        
        # Days past due metrics
        if 'days_past_due' in loan_df.columns:
            metrics['average_days_past_due'] = float(loan_df['days_past_due'].mean())
            metrics['max_days_past_due'] = float(loan_df['days_past_due'].max())
            
            # Delinquency buckets
            metrics['dpd_0_30'] = int((loan_df['days_past_due'] <= 30).sum())
            metrics['dpd_31_60'] = int(((loan_df['days_past_due'] > 30) & (loan_df['days_past_due'] <= 60)).sum())
            metrics['dpd_61_90'] = int(((loan_df['days_past_due'] > 60) & (loan_df['days_past_due'] <= 90)).sum())
            metrics['dpd_90_plus'] = int((loan_df['days_past_due'] > 90).sum())
        
        # Delinquent balance
        if 'delinquent' in loan_df.columns and 'balance' in loan_df.columns:
            delinquent_balance = loan_df[loan_df['delinquent'] == 1]['balance'].sum()
            total_balance = loan_df['balance'].sum()
            metrics['delinquent_balance'] = float(delinquent_balance)
            metrics['delinquent_balance_rate'] = float(
                (delinquent_balance / total_balance * 100) if total_balance > 0 else 0.0
            )
        
        return metrics
    
    def calculate_utilization_metrics(self, loan_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate utilization-related metrics.
        
        Args:
            loan_df: DataFrame containing loan data with columns like 'balance', 'credit_limit', etc.
            
        Returns:
            Dictionary of utilization metrics
        """
        metrics = {}
        
        # Credit utilization
        if 'balance' in loan_df.columns and 'credit_limit' in loan_df.columns:
            # Filter out loans with zero or invalid credit limits
            valid_loans = loan_df[loan_df['credit_limit'] > 0]
            
            if len(valid_loans) > 0:
                # Individual utilization rates
                utilization_rates = valid_loans['balance'] / valid_loans['credit_limit']
                metrics['average_utilization_rate'] = float(utilization_rates.mean() * 100)
                metrics['median_utilization_rate'] = float(utilization_rates.median() * 100)
                
                # Portfolio-level utilization
                total_balance = valid_loans['balance'].sum()
                total_limit = valid_loans['credit_limit'].sum()
                metrics['portfolio_utilization_rate'] = float(
                    (total_balance / total_limit * 100) if total_limit > 0 else 0.0
                )
                
                # Utilization buckets
                metrics['utilization_0_25'] = int((utilization_rates <= 0.25).sum())
                metrics['utilization_25_50'] = int(((utilization_rates > 0.25) & (utilization_rates <= 0.50)).sum())
                metrics['utilization_50_75'] = int(((utilization_rates > 0.50) & (utilization_rates <= 0.75)).sum())
                metrics['utilization_75_100'] = int(((utilization_rates > 0.75) & (utilization_rates <= 1.0)).sum())
                metrics['utilization_over_100'] = int((utilization_rates > 1.0).sum())
        
        # Available credit
        if 'credit_limit' in loan_df.columns and 'balance' in loan_df.columns:
            available_credit = (loan_df['credit_limit'] - loan_df['balance']).clip(lower=0)
            metrics['total_available_credit'] = float(available_credit.sum())
            metrics['average_available_credit'] = float(available_credit.mean())
        
        return metrics
    
    def calculate_segment_mix_metrics(self, loan_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate segment mix metrics.
        
        Args:
            loan_df: DataFrame containing loan data with columns like 'segment', 'product_type', etc.
            
        Returns:
            Dictionary of segment mix metrics
        """
        metrics = {}
        
        total_loans = len(loan_df)
        
        # Segment distribution by count
        if 'segment' in loan_df.columns:
            segment_counts = loan_df['segment'].value_counts()
            for segment, count in segment_counts.items():
                metrics[f'segment_{segment}_count'] = int(count)
                metrics[f'segment_{segment}_pct'] = float(count / total_loans * 100) if total_loans > 0 else 0.0
        
        # Segment distribution by balance
        if 'segment' in loan_df.columns and 'balance' in loan_df.columns:
            total_balance = loan_df['balance'].sum()
            segment_balance = loan_df.groupby('segment')['balance'].sum()
            for segment, balance in segment_balance.items():
                metrics[f'segment_{segment}_balance'] = float(balance)
                metrics[f'segment_{segment}_balance_pct'] = float(
                    (balance / total_balance * 100) if total_balance > 0 else 0.0
                )
        
        # Product type distribution
        if 'product_type' in loan_df.columns:
            product_counts = loan_df['product_type'].value_counts()
            for product, count in product_counts.items():
                metrics[f'product_{product}_count'] = int(count)
                metrics[f'product_{product}_pct'] = float(count / total_loans * 100) if total_loans > 0 else 0.0
        
        return metrics
    
    def calculate_vintage_metrics(self, loan_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate vintage-related metrics.
        
        Args:
            loan_df: DataFrame containing loan data with columns like 'origination_date', 'loan_age', etc.
            
        Returns:
            Dictionary of vintage metrics
        """
        metrics = {}
        
        # Loan age metrics
        if 'loan_age' in loan_df.columns:
            metrics['average_loan_age'] = float(loan_df['loan_age'].mean())
            metrics['median_loan_age'] = float(loan_df['loan_age'].median())
            metrics['max_loan_age'] = float(loan_df['loan_age'].max())
            metrics['min_loan_age'] = float(loan_df['loan_age'].min())
        
        # Origination date metrics
        if 'origination_date' in loan_df.columns:
            # Convert to datetime if not already
            orig_dates = pd.to_datetime(loan_df['origination_date'])
            
            metrics['earliest_origination'] = orig_dates.min().isoformat()
            metrics['latest_origination'] = orig_dates.max().isoformat()
            
            # Vintage year distribution
            vintage_years = orig_dates.dt.year.value_counts().sort_index()
            for year, count in vintage_years.items():
                metrics[f'vintage_{year}_count'] = int(count)
        
        # Maturity metrics
        if 'maturity_date' in loan_df.columns:
            maturity_dates = pd.to_datetime(loan_df['maturity_date'])
            metrics['earliest_maturity'] = maturity_dates.min().isoformat()
            metrics['latest_maturity'] = maturity_dates.max().isoformat()
            
            # Calculate remaining term
            current_date = pd.Timestamp.now()
            remaining_term = (maturity_dates - current_date).dt.days
            metrics['average_remaining_term_days'] = float(remaining_term.mean())
        
        # Weighted average maturity
        if 'maturity_date' in loan_df.columns and 'balance' in loan_df.columns:
            maturity_dates = pd.to_datetime(loan_df['maturity_date'])
            current_date = pd.Timestamp.now()
            remaining_days = (maturity_dates - current_date).dt.days
            
            total_balance = loan_df['balance'].sum()
            if total_balance > 0:
                weighted_maturity = (remaining_days * loan_df['balance']).sum() / total_balance
                metrics['weighted_average_maturity_days'] = float(weighted_maturity)
        
        return metrics


def _require_df(df: pd.DataFrame, name: str) -> None:
    """
    Validate that the input is a non-empty pandas DataFrame.
    
    Args:
        df: The DataFrame to validate
        name: Name of the DataFrame for error messages
        
    Raises:
        ValueError: If df is not a non-empty pandas DataFrame
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError(f"{name} must be a non-empty pandas DataFrame")


def calculate_comprehensive_kpis(loan_df: pd.DataFrame, config: Optional[KPIConfig] = None) -> Dict[str, Any]:
    """
    Calculate comprehensive KPIs for loan portfolio.
    
    Args:
        loan_df: DataFrame containing loan data
        config: Optional KPIConfig for customizing calculations
        
    Returns:
        Dictionary containing all calculated KPIs
        
    Raises:
        ValueError: If loan_df is not a non-empty pandas DataFrame
    """
    _require_df(loan_df, "loan_df")
    return ComprehensiveKPICalculator(config).calculate_all_kpis(loan_df)


def calculate_exposure_metrics(loan_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate exposure-related metrics.
    
    Args:
        loan_df: DataFrame containing loan data
        
    Returns:
        Dictionary of exposure metrics
        
    Raises:
        ValueError: If loan_df is not a non-empty pandas DataFrame
    """
    _require_df(loan_df, "loan_df")
    return ComprehensiveKPICalculator().calculate_exposure_metrics(loan_df)


def calculate_yield_metrics(loan_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate yield-related metrics.
    
    Args:
        loan_df: DataFrame containing loan data
        
    Returns:
        Dictionary of yield metrics
        
    Raises:
        ValueError: If loan_df is not a non-empty pandas DataFrame
    """
    _require_df(loan_df, "loan_df")
    return ComprehensiveKPICalculator().calculate_yield_metrics(loan_df)


def calculate_delinquency_metrics(loan_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate delinquency-related metrics.
    
    Args:
        loan_df: DataFrame containing loan data
        
    Returns:
        Dictionary of delinquency metrics
        
    Raises:
        ValueError: If loan_df is not a non-empty pandas DataFrame
    """
    _require_df(loan_df, "loan_df")
    return ComprehensiveKPICalculator().calculate_delinquency_metrics(loan_df)


def calculate_utilization_metrics(loan_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate utilization-related metrics.
    
    Args:
        loan_df: DataFrame containing loan data
        
    Returns:
        Dictionary of utilization metrics
        
    Raises:
        ValueError: If loan_df is not a non-empty pandas DataFrame
    """
    _require_df(loan_df, "loan_df")
    return ComprehensiveKPICalculator().calculate_utilization_metrics(loan_df)


def calculate_segment_mix_metrics(loan_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate segment mix metrics.
    
    Args:
        loan_df: DataFrame containing loan data
        
    Returns:
        Dictionary of segment mix metrics
        
    Raises:
        ValueError: If loan_df is not a non-empty pandas DataFrame
    """
    _require_df(loan_df, "loan_df")
    return ComprehensiveKPICalculator().calculate_segment_mix_metrics(loan_df)


def calculate_vintage_metrics(loan_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate vintage-related metrics.
    
    Args:
        loan_df: DataFrame containing loan data
        
    Returns:
        Dictionary of vintage metrics
        
    Raises:
        ValueError: If loan_df is not a non-empty pandas DataFrame
    """
    _require_df(loan_df, "loan_df")
    return ComprehensiveKPICalculator().calculate_vintage_metrics(loan_df)
