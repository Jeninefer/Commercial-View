import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from run import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns expected structure."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "datasets" in data

def test_loan_data_pagination():
    """Test loan data endpoint with pagination."""
    response = client.get("/loan-data?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) <= 10

def test_portfolio_summary():
    """Test portfolio summary endpoint."""
    response = client.get("/portfolio-summary")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "by_status" in data
    assert "concentration_metrics" in data

def test_dpd_analysis():
    """Test DPD analysis endpoint."""
    response = client.get("/dpd-analysis")
    assert response.status_code == 200
    data = response.json()
    assert "buckets" in data
    assert "metrics" in data

def test_invalid_endpoint():
    """Test handling of invalid endpoints."""
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

def test_data_quality_endpoint():
    """Test data quality report endpoint."""
    response = client.get("/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "datasets" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
