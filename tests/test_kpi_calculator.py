"""
Tests for the KPICalculator class.
"""

import pytest
import pandas as pd
from abaco_core import KPICalculator


class TestKPICalculator:
    """Test suite for KPICalculator class."""
    
    def test_compute_viability_index_with_startup_metrics(self):
        """Test viability calculation with startup metrics."""
        calculator = KPICalculator()
        
        # Good startup metrics (should score well)
        startup_metrics = {
            'runway_months': 18,
            'burn_rate': 50000,
            'revenue_growth': 0.15,
            'revenue': 80000
        }
        
        viability = calculator.compute_viability_index(startup_metrics=startup_metrics)
        
        # Should be between 0 and 1
        assert 0.0 <= viability <= 1.0
        
        # With good metrics, should be > 0
        assert viability > 0.0
    
    def test_compute_viability_index_without_startup_metrics(self):
        """Test viability calculation without startup metrics (pure fintech case)."""
        calculator = KPICalculator()
        
        # Case 1: No startup metrics at all
        viability = calculator.compute_viability_index(startup_metrics=None)
        assert viability == 0.0  # Not applicable, not "not viable"
        
        # Case 2: Empty startup metrics dict
        viability = calculator.compute_viability_index(startup_metrics={})
        assert viability == 0.0  # Not applicable
        
        # Case 3: Only loan metrics, no startup metrics
        loan_metrics = {'default_rate': 0.02, 'avg_interest': 0.08}
        viability = calculator.compute_viability_index(
            loan_metrics=loan_metrics,
            startup_metrics=None
        )
        assert viability == 0.0  # Not applicable
    
    def test_compute_viability_index_with_custom_thresholds(self):
        """Test viability calculation with custom thresholds."""
        calculator = KPICalculator()
        
        startup_metrics = {
            'runway_months': 15,
            'burn_rate': 80000,
            'revenue_growth': 0.12,
            'revenue': 70000
        }
        
        # Stricter thresholds
        strict_thresholds = {
            'min_runway_months': 18,
            'max_burn_rate': 60000,
            'min_revenue_growth': 0.15,
            'min_revenue': 100000
        }
        
        viability_strict = calculator.compute_viability_index(
            startup_metrics=startup_metrics,
            thresholds=strict_thresholds
        )
        
        # Lenient thresholds
        lenient_thresholds = {
            'min_runway_months': 12,
            'max_burn_rate': 100000,
            'min_revenue_growth': 0.10,
            'min_revenue': 50000
        }
        
        viability_lenient = calculator.compute_viability_index(
            startup_metrics=startup_metrics,
            thresholds=lenient_thresholds
        )
        
        # Lenient should score higher than strict
        assert viability_lenient > viability_strict
    
    def test_compute_viability_index_perfect_score(self):
        """Test viability calculation with perfect metrics."""
        calculator = KPICalculator()
        
        # All metrics exceed default thresholds
        perfect_metrics = {
            'runway_months': 24,
            'burn_rate': 30000,
            'revenue_growth': 0.30,
            'revenue': 200000
        }
        
        viability = calculator.compute_viability_index(startup_metrics=perfect_metrics)
        
        # Should achieve perfect score
        assert viability == 1.0
    
    def test_compute_viability_index_poor_score(self):
        """Test viability calculation with poor metrics."""
        calculator = KPICalculator()
        
        # All metrics below default thresholds
        poor_metrics = {
            'runway_months': 6,
            'burn_rate': 150000,
            'revenue_growth': 0.02,
            'revenue': 20000
        }
        
        viability = calculator.compute_viability_index(startup_metrics=poor_metrics)
        
        # Should score poorly
        assert viability == 0.0
    
    def test_compute_viability_index_partial_metrics(self):
        """Test viability calculation with partial metrics."""
        calculator = KPICalculator()
        
        # Only some metrics provided
        partial_metrics = {
            'runway_months': 18,
            'revenue': 80000
        }
        
        viability = calculator.compute_viability_index(startup_metrics=partial_metrics)
        
        # Should still compute based on available metrics
        assert 0.0 <= viability <= 1.0
    
    def test_calculate_portfolio_kpis_complete(self):
        """Test portfolio KPI calculation with complete data."""
        calculator = KPICalculator()
        
        loans = pd.DataFrame({
            'loan_id': [1, 2, 3, 4, 5],
            'principal': [10000, 20000, 15000, 25000, 30000],
            'interest_rate': [0.08, 0.07, 0.09, 0.06, 0.08],
            'days_past_due': [0, 30, 15, 0, 45]
        })
        
        kpis = calculator.calculate_portfolio_kpis(loans)
        
        # Check expected KPIs
        assert kpis['total_loans'] == 5
        assert kpis['total_principal'] == 100000
        assert kpis['average_loan_size'] == 20000
        assert 'average_interest_rate' in kpis
        assert 'average_dpd' in kpis
    
    def test_calculate_portfolio_kpis_empty(self):
        """Test portfolio KPI calculation with empty dataframe."""
        calculator = KPICalculator()
        
        loans = pd.DataFrame(columns=['loan_id', 'principal', 'interest_rate'])
        
        kpis = calculator.calculate_portfolio_kpis(loans)
        
        # Should handle empty portfolio gracefully
        assert kpis['total_loans'] == 0
    
    def test_calculate_portfolio_kpis_minimal(self):
        """Test portfolio KPI calculation with minimal columns."""
        calculator = KPICalculator()
        
        loans = pd.DataFrame({
            'loan_id': [1, 2, 3]
        })
        
        kpis = calculator.calculate_portfolio_kpis(loans)
        
        # Should still return basic metrics
        assert kpis['total_loans'] == 3
        assert 'total_principal' not in kpis  # Column not present
    
    def test_viability_documentation_requirement(self):
        """Test that viability behavior is as documented for pure fintech case."""
        calculator = KPICalculator()
        
        # Pure fintech with only loan data (no startup metrics)
        loan_only_metrics = {
            'default_rate': 0.02,
            'avg_interest': 0.08,
            'total_loans': 1000
        }
        
        # Should return 0.0 (not applicable) as documented
        viability = calculator.compute_viability_index(
            loan_metrics=loan_only_metrics,
            startup_metrics=None
        )
        
        assert viability == 0.0
        
        # This 0.0 should be interpreted as "viability not applicable"
        # not as "business is not viable"
        # Application logic should document this behavior
