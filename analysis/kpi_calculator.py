"""
KPI calculations module.
Computes key performance indicators for portfolio analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta


class KPICalculator:
    """Calculator for portfolio KPIs."""
    
    def __init__(self, loan_tape: pd.DataFrame):
        self.loan_tape = loan_tape
    
    def calculate_portfolio_apr(self) -> float:
        """
        Calculate weighted average APR of the portfolio.
        """
        if 'principal' not in self.loan_tape.columns or 'apr' not in self.loan_tape.columns:
            return 0.0
        
        active_loans = self.loan_tape[self.loan_tape['status'] == 'active']
        if len(active_loans) == 0:
            return 0.0
        
        total_principal = active_loans['principal'].sum()
        if total_principal == 0:
            return 0.0
        
        weighted_apr = (active_loans['principal'] * active_loans['apr']).sum() / total_principal
        return weighted_apr
    
    def calculate_rotation_speed(self) -> float:
        """
        Calculate average portfolio rotation speed (weighted average term in days).
        """
        if 'principal' not in self.loan_tape.columns or 'term_days' not in self.loan_tape.columns:
            return 0.0
        
        active_loans = self.loan_tape[self.loan_tape['status'] == 'active']
        if len(active_loans) == 0:
            return 0.0
        
        total_principal = active_loans['principal'].sum()
        if total_principal == 0:
            return 0.0
        
        weighted_term = (active_loans['principal'] * active_loans['term_days']).sum() / total_principal
        return weighted_term
    
    def calculate_concentration_risk(self) -> Dict[str, float]:
        """
        Calculate concentration risk by client and sector.
        Returns dictionary with max concentrations.
        """
        if 'principal' not in self.loan_tape.columns:
            return {'client': 0.0, 'sector': 0.0}
        
        active_loans = self.loan_tape[self.loan_tape['status'] == 'active']
        if len(active_loans) == 0:
            return {'client': 0.0, 'sector': 0.0}
        
        total_principal = active_loans['principal'].sum()
        
        # Client concentration
        client_concentration = 0.0
        if 'client_id' in active_loans.columns:
            client_exposure = active_loans.groupby('client_id')['principal'].sum()
            client_concentration = (client_exposure / total_principal).max()
        
        # Sector concentration
        sector_concentration = 0.0
        if 'sector' in active_loans.columns:
            sector_exposure = active_loans.groupby('sector')['principal'].sum()
            sector_concentration = (sector_exposure / total_principal).max()
        
        return {
            'client': client_concentration,
            'sector': sector_concentration
        }
    
    def calculate_dpd_metrics(self) -> Dict[str, Any]:
        """
        Calculate Days Past Due metrics.
        """
        if 'dpd' not in self.loan_tape.columns:
            return {'avg_dpd': 0.0, 'max_dpd': 0, 'overdue_ratio': 0.0}
        
        active_loans = self.loan_tape[self.loan_tape['status'].isin(['active', 'overdue'])]
        if len(active_loans) == 0:
            return {'avg_dpd': 0.0, 'max_dpd': 0, 'overdue_ratio': 0.0}
        
        avg_dpd = active_loans['dpd'].mean()
        max_dpd = active_loans['dpd'].max()
        overdue_ratio = (active_loans['dpd'] > 0).sum() / len(active_loans)
        
        return {
            'avg_dpd': avg_dpd,
            'max_dpd': max_dpd,
            'overdue_ratio': overdue_ratio
        }
    
    def calculate_mom_growth(self, historical_data: List[Dict[str, Any]] = None) -> float:
        """
        Calculate Month-over-Month revenue growth.
        If historical data not provided, returns 0.
        """
        if historical_data is None or len(historical_data) < 2:
            return 0.0
        
        # Sort by month
        sorted_data = sorted(historical_data, key=lambda x: x['month'])
        
        # Calculate MoM growth from last two months
        current_revenue = sorted_data[-1]['revenue']
        previous_revenue = sorted_data[-2]['revenue']
        
        if previous_revenue == 0:
            return 0.0
        
        growth = (current_revenue - previous_revenue) / previous_revenue
        return growth
    
    def calculate_all_kpis(self, historical_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate all KPIs and return as dictionary.
        """
        concentration = self.calculate_concentration_risk()
        dpd_metrics = self.calculate_dpd_metrics()
        
        return {
            'portfolio_apr': self.calculate_portfolio_apr(),
            'rotation_speed_days': self.calculate_rotation_speed(),
            'client_concentration': concentration['client'],
            'sector_concentration': concentration['sector'],
            'avg_dpd': dpd_metrics['avg_dpd'],
            'max_dpd': dpd_metrics['max_dpd'],
            'overdue_ratio': dpd_metrics['overdue_ratio'],
            'mom_growth': self.calculate_mom_growth(historical_data),
            'total_principal': self.loan_tape[self.loan_tape['status'] == 'active']['principal'].sum() if 'principal' in self.loan_tape.columns else 0,
            'active_loans': len(self.loan_tape[self.loan_tape['status'] == 'active'])
        }
    
    def get_kpi_summary(self, historical_data: List[Dict[str, Any]] = None) -> str:
        """
        Generate a human-readable summary of KPIs.
        """
        kpis = self.calculate_all_kpis(historical_data)
        
        summary = f"""
Portfolio KPI Summary
=====================
Total Active Principal: ${kpis['total_principal']:,.2f}
Active Loans: {kpis['active_loans']}
Weighted Average APR: {kpis['portfolio_apr']*100:.2f}%
Average Rotation Speed: {kpis['rotation_speed_days']:.0f} days

Concentration Risk:
- Max Client Concentration: {kpis['client_concentration']*100:.1f}%
- Max Sector Concentration: {kpis['sector_concentration']*100:.1f}%

Portfolio Quality:
- Average DPD: {kpis['avg_dpd']:.1f} days
- Maximum DPD: {kpis['max_dpd']} days
- Overdue Ratio: {kpis['overdue_ratio']*100:.1f}%

Growth:
- Month-over-Month Growth: {kpis['mom_growth']*100:.1f}%
"""
        return summary


def calculate_portfolio_kpis(loan_tape: pd.DataFrame, historical_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to calculate all portfolio KPIs.
    """
    calculator = KPICalculator(loan_tape)
    return calculator.calculate_all_kpis(historical_data)
