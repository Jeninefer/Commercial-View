"""
Basic tests for the KPI Calculator
"""
import pytest
import pandas as pd
import numpy as np
from abaco_core import KPICalculator


class TestKPICalculator:
    def test_initialization(self):
        """Test KPICalculator initialization"""
        calc = KPICalculator()
        assert calc.export_path == "./abaco_runtime/exports"
        assert calc.thresholds["runway_months_min"] == 12
        assert calc.thresholds["ltv_cac_ratio_min"] == 3.0
        assert calc.thresholds["nrr_min"] == 1.0

    def test_safe_division(self):
        """Test safe division method"""
        calc = KPICalculator()
        
        # Scalar division
        assert calc.safe_division(10, 2) == 5.0
        assert np.isnan(calc.safe_division(10, 0))
        assert calc.safe_division(10, 0, default=0) == 0
        
        # Series division
        num = pd.Series([10, 20, 30])
        den = pd.Series([2, 0, 5])
        result = calc.safe_division(num, den, default=0)
        assert result[0] == 5.0
        assert result[1] == 0.0
        assert result[2] == 6.0

    def test_compute_startup_metrics_basic(self):
        """Test basic startup metrics computation"""
        calc = KPICalculator()
        
        revenue_df = pd.DataFrame({
            "date": ["2023-01-01", "2023-02-01"],
            "recurring_revenue": [10000, 12000]
        })
        
        customer_df = pd.DataFrame({
            "churn_count": [5],
            "start_count": [100]
        })
        
        metrics = calc.compute_startup_metrics(revenue_df, customer_df)
        
        assert "mrr" in metrics
        assert metrics["mrr"] == 12000.0
        assert "arr" in metrics
        assert metrics["arr"] == 12000.0 * 12
        assert "churn_rate" in metrics
        assert metrics["churn_rate"] == 0.05

    def test_compute_fintech_metrics_basic(self):
        """Test basic fintech metrics computation"""
        calc = KPICalculator()
        
        loan_df = pd.DataFrame({
            "loan_amount": [1000, 2000, 3000],
            "days_past_due": [0, 100, 200]
        })
        
        metrics = calc.compute_fintech_metrics(loan_df)
        
        assert "gmv" in metrics
        assert metrics["gmv"] == 6000.0
        assert "default_rate" in metrics
        # 1 loan has dpd >= 180
        assert metrics["default_rate"] == 1/3

    def test_compute_valuation_metrics_basic(self):
        """Test basic valuation metrics computation"""
        calc = KPICalculator()
        
        financial_df = pd.DataFrame({
            "pre_money_valuation": [1000000],
            "investment_amount": [250000],
            "enterprise_value": [1500000]
        })
        
        metrics = calc.compute_valuation_metrics(financial_df)
        
        assert "pre_money_valuation" in metrics
        assert metrics["pre_money_valuation"] == 1000000
        assert "post_money_valuation" in metrics
        assert metrics["post_money_valuation"] == 1250000
        assert "enterprise_value" in metrics
        assert metrics["enterprise_value"] == 1500000

    def test_compute_viability_index(self):
        """Test viability index computation"""
        calc = KPICalculator()
        
        startup_metrics = {
            "runway_months": 24,  # >= 2 * 12 (max score)
            "ltv_cac_ratio": 6,   # >= 2 * 3 (max score)
            "nrr": 1.2            # >= 1.2 * 1.0 (max score)
        }
        
        viability = calc.compute_viability_index(startup_metrics)
        assert viability == 100

    def test_compute_kpis_orchestrator(self):
        """Test the main KPI orchestrator"""
        calc = KPICalculator()
        
        data_dict = {
            "revenue": pd.DataFrame({
                "date": ["2023-01-01"],
                "recurring_revenue": [10000]
            }),
            "customer": pd.DataFrame({
                "churn_count": [5],
                "start_count": [100]
            })
        }
        
        result = calc.compute_kpis(data_dict)
        
        assert "startup" in result
        assert "fintech" in result
        assert "valuation" in result
        assert "viability" in result
        assert "mrr" in result["startup"]

    def test_summarize_kpis(self):
        """Test KPI summarization"""
        calc = KPICalculator()
        
        metrics = {
            "startup": {"mrr": 10000, "arr": 120000, "churn_rate": 0.05},
            "fintech": {"gmv": 50000, "default_rate": 0.02},
            "valuation": {"enterprise_value": 1000000},
            "viability": {"viability_index": 75}
        }
        
        summary = calc.summarize_kpis(metrics)
        
        assert "mrr" in summary
        assert "gmv" in summary
        assert "enterprise_value" in summary
        assert "viability_index" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
