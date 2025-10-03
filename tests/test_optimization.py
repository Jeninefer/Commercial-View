"""
Test optimization module.
"""

import pytest
import pandas as pd
from optimization import DisbursementOptimizer, optimize_disbursements


@pytest.fixture
def sample_portfolio():
    """Create sample portfolio."""
    return pd.DataFrame({
        'loan_id': ['L001', 'L002', 'L003'],
        'client_id': ['C001', 'C002', 'C003'],
        'principal': [100000, 150000, 75000],
        'apr': [0.15, 0.18, 0.12],
        'status': ['active', 'active', 'active'],
        'sector': ['Retail', 'Tech', 'Services']
    })


@pytest.fixture
def sample_requests():
    """Create sample disbursement requests."""
    return pd.DataFrame({
        'request_id': ['R001', 'R002', 'R003', 'R004'],
        'client_id': ['C001', 'C004', 'C005', 'C006'],
        'client_name': ['Client 1', 'Client 4', 'Client 5', 'Client 6'],
        'requested_amount': [50000, 100000, 75000, 125000],
        'proposed_apr': [0.16, 0.19, 0.14, 0.17],
        'proposed_term': [90, 60, 120, 90],
        'sector': ['Retail', 'Tech', 'Manufacturing', 'Services'],
        'credit_score': [750, 680, 720, 700]
    })


def test_optimizer_init(sample_requests, sample_portfolio):
    """Test optimizer initialization."""
    optimizer = DisbursementOptimizer(
        disbursement_requests=sample_requests,
        current_portfolio=sample_portfolio,
        available_cash=200000
    )
    
    assert optimizer.available_cash == 200000
    assert len(optimizer.requests) == 4
    assert len(optimizer.portfolio) == 3


def test_greedy_optimization(sample_requests, sample_portfolio):
    """Test greedy optimization."""
    optimizer = DisbursementOptimizer(
        disbursement_requests=sample_requests,
        current_portfolio=sample_portfolio,
        available_cash=200000
    )
    
    result = optimizer.optimize_greedy()
    
    assert 'status' in result
    assert 'selected_loans' in result
    assert 'total_disbursement' in result
    assert result['total_disbursement'] <= 200000


def test_optimization_scores(sample_requests, sample_portfolio):
    """Test that scores are calculated."""
    optimizer = DisbursementOptimizer(
        disbursement_requests=sample_requests,
        current_portfolio=sample_portfolio,
        available_cash=150000
    )
    
    result = optimizer.generate_recommendation(method='greedy')
    
    assert 'expected_kpis' in result
    kpis = result['expected_kpis']
    
    assert 'apr_score' in kpis
    assert 'rotation_score' in kpis
    assert 'concentration_score' in kpis
    assert 'growth_score' in kpis
    assert 'dpd_score' in kpis
    assert 'overall_score' in kpis
    
    # All scores should be between 0 and 1
    for score in kpis.values():
        assert 0 <= score <= 1


def test_cash_constraint(sample_requests, sample_portfolio):
    """Test that optimization respects cash constraint."""
    optimizer = DisbursementOptimizer(
        disbursement_requests=sample_requests,
        current_portfolio=sample_portfolio,
        available_cash=100000
    )
    
    result = optimizer.optimize_greedy()
    
    assert result['total_disbursement'] <= 100000


def test_optimize_disbursements_function(sample_requests, sample_portfolio):
    """Test convenience function."""
    result = optimize_disbursements(
        requests=sample_requests,
        portfolio=sample_portfolio,
        available_cash=200000,
        method='greedy'
    )
    
    assert isinstance(result, dict)
    assert 'selected_loans' in result
    assert 'num_loans' in result
    assert 'cash_utilization' in result
