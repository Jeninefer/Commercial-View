"""
Integration tests for Commercial-View Analytics API
Tests comprehensive dashboard endpoints
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from src.run_simple import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "data_available" in data
    assert "timestamp" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_executive_summary():
    """Test executive summary endpoint"""
    response = client.get("/executive-summary")
    assert response.status_code == 200
    data = response.json()
    
    # Check required sections
    assert "portfolio_overview" in data
    assert "risk_indicators" in data
    assert "tenor_distribution" in data
    assert "performance_metrics" in data
    
    # Check portfolio overview metrics
    portfolio = data["portfolio_overview"]
    assert "total_portfolio_value" in portfolio
    assert "active_loan_count" in portfolio
    assert "weighted_average_rate" in portfolio


def test_portfolio_trends():
    """Test portfolio trends endpoint"""
    response = client.get("/portfolio/trends")
    assert response.status_code == 200
    data = response.json()
    
    assert "trends" in data
    trends = data["trends"]
    
    # Check trend data structure
    assert "portfolio_growth" in trends
    assert "labels" in trends["portfolio_growth"]
    assert "values" in trends["portfolio_growth"]


def test_risk_exposure():
    """Test risk exposure endpoint"""
    response = client.get("/portfolio/risk-exposure")
    assert response.status_code == 200
    data = response.json()
    
    # Check required sections
    assert "risk_summary" in data
    assert "risk_distribution" in data
    assert "concentration_risk" in data
    assert "dpd_distribution" in data
    
    # Check risk summary
    risk_summary = data["risk_summary"]
    assert "total_exposure" in risk_summary
    assert "at_risk_amount" in risk_summary
    assert "at_risk_percentage" in risk_summary


def test_csv_ingestion_no_file():
    """Test CSV ingestion without file"""
    response = client.post("/portfolio/ingest")
    # Should return validation error
    assert response.status_code == 422


def test_api_documentation():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
