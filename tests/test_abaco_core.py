"""
Basic tests for ABACO Core Library
"""
import pytest
import pandas as pd
import numpy as np
from abaco_core.manifest import (
    bucket_apr, bucket_line, bucket_payer, classify_client, map_naics, share
)
from abaco_core.optimizer import DisbursementOptimizer
from abaco_core.alerts import Alert, AlertEngine


class TestManifest:
    """Test manifest functions."""
    
    def test_bucket_apr(self):
        assert bucket_apr(10.0) == "0-15%"
        assert bucket_apr(18.5) == "15-20%"
        assert bucket_apr(22.0) == "20-25%"
        assert bucket_apr(27.5) == "25-30%"
        assert bucket_apr(35.0) == "30%+"
    
    def test_bucket_line(self):
        assert bucket_line(50_000) == "0-100k"
        assert bucket_line(150_000) == "100k-250k"
        assert bucket_line(350_000) == "250k-500k"
        assert bucket_line(750_000) == "500k-1M"
        assert bucket_line(2_500_000) == "1M-5M"
        assert bucket_line(7_000_000) == "5M+"
    
    def test_bucket_payer(self):
        assert bucket_payer(3.0) == "A"
        assert bucket_payer(10.0) == "B"
        assert bucket_payer(20.0) == "C"
        assert bucket_payer(35.0) == "D"
    
    def test_classify_client(self):
        assert classify_client(3_000_000, 2) == "startup"
        assert classify_client(25_000_000, 5) == "growing"
        assert classify_client(75_000_000, 10) == "enterprise"
    
    def test_map_naics(self):
        assert "Professional" in map_naics("541512")
        assert "Manufacturing" in map_naics("33")
        assert "Retail" in map_naics("44")
        assert map_naics("99") == "Unknown Industry"
    
    def test_share(self):
        series = pd.Series({"A": 100, "B": 200, "C": 200})
        result = share(series)
        assert abs(result["A"] - 20.0) < 0.01
        assert abs(result["B"] - 40.0) < 0.01
        assert abs(result["C"] - 40.0) < 0.01


class TestOptimizer:
    """Test optimizer functionality."""
    
    def test_optimizer_basic(self):
        optimizer = DisbursementOptimizer()
        
        # Create test data
        requests = pd.DataFrame({
            "amount": [100_000, 200_000],
            "apr": [20.0, 25.0],
            "industry": ["Tech", "Retail"],
            "payer_grade": ["A", "B"],
            "customer_id": ["C001", "C002"],
        })
        
        current_portfolio = pd.DataFrame({
            "amount": [500_000],
            "apr": [22.0],
            "industry": ["Manufacturing"],
            "payer_grade": ["A"],
            "customer_id": ["C003"],
        })
        
        selected, report = optimizer.optimize(
            requests=requests,
            current_portfolio=current_portfolio,
            aum_target=1_000_000,
        )
        
        assert report["budget"] == 500_000
        assert report["selected_count"] >= 0
        assert report["selected_amount"] <= report["budget"]
    
    def test_score_request(self):
        optimizer = DisbursementOptimizer(
            top_client_max=0.15,
            industry_max_share=0.25,
        )
        
        current_portfolio = pd.DataFrame({
            "amount": [500_000],
            "apr": [22.0],
            "industry": ["Manufacturing"],
            "payer_grade": ["A"],
            "customer_id": ["C001"],
        })
        
        # Good request (A-grade payer, won't exceed limits)
        score = optimizer.score_request(
            amount=50_000,  # Small enough to not trigger concentration limit
            apr=20.0,
            industry="Tech",
            payer_grade="A",
            customer_id="C002",
            current_portfolio=current_portfolio,
        )
        assert score > 0
        
        # Bad request (exceeds top client limit)
        score = optimizer.score_request(
            amount=1_000_000,  # Would be > 15% of portfolio
            apr=20.0,
            industry="Tech",
            payer_grade="A",
            customer_id="C001",  # Same as existing client
            current_portfolio=current_portfolio,
        )
        assert score < 0  # Should be rejected


class TestAlerts:
    """Test alert engine."""
    
    def test_alert_creation(self):
        alert = Alert(
            severity="warning",
            category="concentration",
            title="Test Alert",
            message="This is a test",
            value=100.0,
            threshold=80.0,
        )
        
        assert alert.severity == "warning"
        assert alert.category == "concentration"
        assert alert.value == 100.0
        
        # Test to_dict
        d = alert.to_dict()
        assert d["title"] == "Test Alert"
        
        # Test to_slack_block
        block = alert.to_slack_block()
        assert block["type"] == "section"
        assert "Test Alert" in block["text"]["text"]
    
    def test_concentration_alerts(self):
        engine = AlertEngine()
        
        exposures = pd.Series({
            "C001": 1_000_000,  # 50% - should trigger
            "C002": 500_000,
            "C003": 300_000,
            "C004": 200_000,
        })
        
        alerts = engine.concentration_alerts(
            exposures,
            top_1_threshold=0.15,
            top_5_threshold=0.40,
        )
        
        # Should have at least one alert for top client concentration
        assert len(alerts) > 0
        assert any(a.category == "concentration" for a in alerts)
    
    def test_risk_alerts(self):
        engine = AlertEngine()
        
        # High NPL increase should trigger alert
        alerts = engine.risk_alerts(
            npl180_mom_bps=100,  # 100 bps increase
            dpd_7d_growth=2.0,  # 2x growth
        )
        
        assert len(alerts) > 0
        assert any(a.category == "risk" for a in alerts)
    
    def test_yield_alerts(self):
        engine = AlertEngine()
        
        apr_mix = pd.Series({"15-20%": 40, "20-25%": 30, "25-30%": 30})
        target = {"15-20%": 30, "20-25%": 40, "25-30%": 30}
        
        alerts = engine.yield_alerts(
            apr_mix=apr_mix,
            target_apr_mix=target,
            deviation_threshold=5.0,
        )
        
        # Should detect deviation in 15-20% bucket
        assert len(alerts) > 0
        assert any("15-20%" in a.title for a in alerts)
    
    def test_liquidity_alerts(self):
        engine = AlertEngine()
        
        alerts = engine.liquidity_alerts(
            collections_vs_plan=0.80,  # 80% of plan
            bank_shortfall=True,
        )
        
        # Should have alerts for both conditions
        assert len(alerts) == 2
        assert any(a.category == "liquidity" for a in alerts)
    
    def test_growth_alerts(self):
        engine = AlertEngine()
        
        alerts = engine.growth_alerts(
            ltv_over_3_cac=False,
            payback_months=20.0,
        )
        
        # Should have alerts for both conditions
        assert len(alerts) == 2
        assert any(a.category == "growth" for a in alerts)
    
    def test_ewma(self):
        engine = AlertEngine(ewma_alpha=0.3)
        series = pd.Series([100, 105, 110, 115, 120])
        ewma = engine._ewma(series)
        
        assert len(ewma) == len(series)
        assert ewma.iloc[-1] > ewma.iloc[0]  # Should trend upward
    
    def test_cusum(self):
        engine = AlertEngine()
        series = pd.Series([0, 1, 2, 3, 4])
        cusum = engine._cusum(series, target=0.0)
        
        assert len(cusum) == len(series)
        assert cusum.iloc[-1] > cusum.iloc[0]  # Should accumulate
    
    def test_mad_z_score(self):
        engine = AlertEngine()
        series = pd.Series([100, 102, 98, 101, 99, 103])
        
        # Normal value
        z = engine._mad_z_score(101, series)
        assert abs(z) < 2.0
        
        # Outlier
        z = engine._mad_z_score(150, series)
        assert abs(z) > 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
