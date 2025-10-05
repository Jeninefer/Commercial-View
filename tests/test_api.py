import os
import sys

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import run


def build_sample_dataframe() -> pd.DataFrame:
    """Create a reusable dataframe used across dataset fixtures."""
    return pd.DataFrame(
        {
            "loan_id": ["L001", "L002", "L003"],
            "customer_id": ["C001", "C002", "C003"],
            "loan_status": ["Current", "Complete", "Default"],
            "outstanding_balance": [1000.0, 0.0, 500.0],
            "interest_rate": [0.05, 0.06, 0.07],
            "days_past_due": [0, 15, 45],
            "payment_amount": [100.0, 150.0, 200.0],
            "due_date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "True Payment Status": ["Paid", "Pending", "Late"],
        }
    )


@pytest.fixture(scope="module")
def dataset_dict() -> dict:
    base_df = build_sample_dataframe()
    return {
        "loan_data": base_df[
            [
                "loan_id",
                "customer_id",
                "loan_status",
                "outstanding_balance",
                "interest_rate",
                "days_past_due",
            ]
        ].copy(),
        "payment_schedule": base_df[["loan_id", "payment_amount", "due_date"]].copy(),
        "historic_real_payment": base_df[
            ["loan_id", "True Payment Status", "payment_amount"]
        ].copy(),
    }


@pytest.fixture(scope="module")
def client(dataset_dict):
    """Create a TestClient that uses a stubbed data loader."""

    class StubDataLoader:
        def __init__(self, *_args, **_kwargs):
            self._datasets = dataset_dict

        def load_all_datasets(self):
            return self._datasets

        def get_data_quality_report(self):
            return {"status": "not implemented"}

    original_loader = run.DataLoader
    original_datasets = run.datasets
    original_data_loader_instance = getattr(run, "data_loader", None)

    run.datasets = dataset_dict
    run.DataLoader = StubDataLoader
    run.data_loader = None

    try:
        with TestClient(run.app) as test_client:
            yield test_client
    finally:
        run.DataLoader = original_loader
        run.datasets = original_datasets
        run.data_loader = original_data_loader_instance

def test_root_endpoint(client):
    """Test the root endpoint returns expected structure."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_health_endpoint(client, dataset_dict):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "datasets" in data
    assert set(dataset_dict.keys()).issubset(data["datasets"].keys())

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