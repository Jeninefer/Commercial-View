import pytest
from fastapi.testclient import TestClient
import sys
import os
import pandas as pd
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import PRICING_FILENAMES

@pytest.fixture(scope="module")
def test_data_path(tmp_path_factory):
    """Create a temporary directory with dummy data files."""
    base_dir = tmp_path_factory.mktemp("data") / "pricing"
    base_dir.mkdir()

    sample_df = pd.DataFrame(
        {
            "id": [1, 2],
            "value": [100, 200],
            "loan_id": ["L001", "L002"],
            "customer_id": ["C001", "C002"],
            "loan_status": ["Current", "Complete"],
            "outstanding_balance": [1000, 0],
            "interest_rate": [0.05, 0.06],
            "days_past_due": [0, 0],
        }
    )

    for filename in PRICING_FILENAMES.values():
        sample_df.to_csv(base_dir / filename, index=False)

    return str(base_dir)

@pytest.fixture(scope="module")
def client(test_data_path):
    """A TestClient instance that uses a temporary data directory."""
    os.environ["COMMERCIAL_VIEW_DATA_PATH"] = test_data_path
    from run import app
    with TestClient(app) as c:
        yield c

def test_root_endpoint(client):
    """Test the root endpoint returns expected structure."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "datasets" in data
    assert len(data["datasets"]) == len(PRICING_FILENAMES)

def test_loan_data_pagination(client):
    """Test loan data endpoint with pagination."""
    response = client.get("/loan-data?skip=0&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 1

def test_portfolio_summary(client):
    """Test portfolio summary endpoint."""
    response = client.get("/portfolio-summary")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "by_status" in data
    assert "concentration_metrics" in data

def test_dpd_analysis(client):
    """Test DPD analysis endpoint."""
    response = client.get("/dpd-analysis")
    assert response.status_code == 200
    data = response.json()
    assert "buckets" in data
    assert "metrics" in data

def test_invalid_endpoint(client):
    """Test handling of invalid endpoints."""
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

def test_data_quality_endpoint(client):
    """Test data quality report endpoint."""
    response = client.get("/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "not implemented"}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])