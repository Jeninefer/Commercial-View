"""
Test analysis module.
"""

import pytest
import pandas as pd
import numpy as np
from analysis import KPICalculator, calculate_portfolio_kpis


@pytest.fixture
def sample_loan_tape():
    """Create sample loan tape for testing."""
    return pd.DataFrame({
        'loan_id': ['L001', 'L002', 'L003', 'L004', 'L005'],
        'client_id': ['C001', 'C002', 'C001', 'C003', 'C004'],
        'principal': [100000, 150000, 75000, 200000, 50000],
        'apr': [0.15, 0.18, 0.12, 0.20, 0.10],
        'term_days': [90, 60, 120, 90, 30],
        'status': ['active', 'active', 'active', 'paid', 'overdue'],
        'dpd': [0, 0, 5, 0, 15],
        'sector': ['Retail', 'Tech', 'Retail', 'Services', 'Manufacturing']
    })


def test_kpi_calculator_init(sample_loan_tape):
    """Test KPI calculator initialization."""
    calculator = KPICalculator(sample_loan_tape)
    assert calculator.loan_tape is not None
    assert len(calculator.loan_tape) == 5


def test_portfolio_apr(sample_loan_tape):
    """Test portfolio APR calculation."""
    calculator = KPICalculator(sample_loan_tape)
    apr = calculator.calculate_portfolio_apr()
    
    # Should calculate weighted average APR for active loans
    assert isinstance(apr, float)
    assert 0 <= apr <= 1


def test_rotation_speed(sample_loan_tape):
    """Test rotation speed calculation."""
    calculator = KPICalculator(sample_loan_tape)
    rotation = calculator.calculate_rotation_speed()
    
    assert isinstance(rotation, float)
    assert rotation > 0


def test_concentration_risk(sample_loan_tape):
    """Test concentration risk calculation."""
    calculator = KPICalculator(sample_loan_tape)
    concentration = calculator.calculate_concentration_risk()
    
    assert isinstance(concentration, dict)
    assert 'client' in concentration
    assert 'sector' in concentration
    assert 0 <= concentration['client'] <= 1
    assert 0 <= concentration['sector'] <= 1


def test_dpd_metrics(sample_loan_tape):
    """Test DPD metrics calculation."""
    calculator = KPICalculator(sample_loan_tape)
    dpd_metrics = calculator.calculate_dpd_metrics()
    
    assert isinstance(dpd_metrics, dict)
    assert 'avg_dpd' in dpd_metrics
    assert 'max_dpd' in dpd_metrics
    assert 'overdue_ratio' in dpd_metrics


def test_calculate_all_kpis(sample_loan_tape):
    """Test calculating all KPIs."""
    calculator = KPICalculator(sample_loan_tape)
    kpis = calculator.calculate_all_kpis()
    
    assert isinstance(kpis, dict)
    assert 'portfolio_apr' in kpis
    assert 'rotation_speed_days' in kpis
    assert 'client_concentration' in kpis
    assert 'sector_concentration' in kpis
    assert 'total_principal' in kpis
    assert 'active_loans' in kpis


def test_calculate_portfolio_kpis_function(sample_loan_tape):
    """Test convenience function."""
    kpis = calculate_portfolio_kpis(sample_loan_tape)
    
    assert isinstance(kpis, dict)
    assert len(kpis) > 0
