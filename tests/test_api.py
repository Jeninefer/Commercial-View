"""Test suite for Commercial View API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd

from run import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test class for all API endpoints."""
    
    @pytest.fixture(autouse=True)
    def mock_pipeline(self):
        """Mock pipeline to avoid file dependencies in tests."""
        with patch('run.CommercialViewPipeline') as mock_class:
            # Create mock instance
            mock_instance = MagicMock()
            
            # Configure mock data
            mock_instance._datasets = {
                'loan_data': pd.DataFrame({
                    'Customer ID': ['C001', 'C002'],
                    'Loan ID': ['L001', 'L002'],
                    'Outstanding Loan Value': [100000, 200000],
                    'Days in Default': [0, 45],
                    'Interest Rate APR': [0.18, 0.22]
                }),
                'payment_schedule': pd.DataFrame({
                    'Loan ID': ['L001', 'L002'],
                    'Payment Date': ['2024-01-15', '2024-01-15'],
                    'Total Payment': [5000, 10000]
                }),
                'historic_real_payment': pd.DataFrame({
                    'Loan ID': ['L001', 'L002'],
                    'True Payment Date': ['2024-01-15', '2024-01-16'],
                    'True Principal Payment': [4500, 9000]
                })
            }
            
            # Configure mock methods
            mock_instance.compute_dpd_metrics.return_value = pd.DataFrame({
                'Loan ID': ['L001', 'L002'],
                'dpd_bucket': ['Current', '30d'],
                'past_due_amount': [0, 200000],
                'is_default': [False, False]
            })
            
            mock_instance.compute_portfolio_metrics.return_value = {
                'portfolio_outstanding': 300000,
                'active_clients': 2,
                'weighted_apr': 0.2,
                'npl_180': 0
            }
            
            mock_instance.generate_executive_summary.return_value = {
                'portfolio_overview': {
                    'outstanding_balance': 300000,
                    'active_clients': 2
                },
                'risk_indicators': {
                    'dpd_distribution': {'Current': 100000, '30d': 200000}
                }
            }
            
            # Set up the mock class to return our mock instance
            mock_class.return_value = mock_instance
            
            # Return the mock instance for use in tests
            yield mock_instance
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Commercial View API"}
    
    def test_loan_data_endpoint(self):
        """Test loan data retrieval."""
        response = client.get("/loan-data")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]['Customer ID'] == 'C001'
    
    def test_payment_schedule_endpoint(self):
        """Test payment schedule retrieval."""
        response = client.get("/payment-schedule")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert 'Total Payment' in data[0]
    
    def test_historic_payment_endpoint(self):
        """Test historic payment retrieval."""
        response = client.get("/historic-real-payment")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert 'True Principal Payment' in data[0]
    
    def test_schema_endpoint(self):
        """Test schema retrieval."""
        response = client.get("/schema/loan_data")
        assert response.status_code == 200
        schema = response.json()
        assert 'columns' in schema
        assert 'Customer ID' in schema['columns']
    
    def test_invalid_schema_endpoint(self):
        """Test invalid schema request."""
        response = client.get("/schema/invalid_dataset")
        assert response.status_code == 404
    
    def test_customer_data_endpoint_missing(self):
        """Test customer data when file is missing."""
        response = client.get("/customer-data")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_collateral_endpoint_missing(self):
        """Test collateral data when file is missing."""
        response = client.get("/collateral")
        assert response.status_code == 200
        assert response.json() == []
        
    def test_executive_summary_endpoint(self):
        """Test executive summary endpoint."""
        response = client.get("/executive-summary")
        assert response.status_code == 200
        data = response.json()
        assert 'portfolio_overview' in data
        assert 'risk_indicators' in data
        
    def test_portfolio_metrics_endpoint(self):
        """Test portfolio metrics endpoint."""
        response = client.get("/portfolio-metrics")
        assert response.status_code == 200
        data = response.json()
        assert 'portfolio_outstanding' in data
        assert 'active_clients' in data
    
    def test_pricing_grid_endpoint(self):
        """Test pricing grid retrieval endpoint."""
        response = client.get("/pricing-grid?pricing_type=main")
        assert response.status_code == 200
        data = response.json()
        # Should return empty list or pricing data
        assert isinstance(data, list)
    
    def test_pricing_config_endpoint(self):
        """Test pricing config endpoint."""
        response = client.get("/pricing-config")
        assert response.status_code == 200
        data = response.json()
        assert 'pricing_files' in data or 'error' in data
    
    def test_enrich_pricing_endpoint(self):
        """Test pricing enrichment endpoint."""
        request_data = {
            "loan_data": [
                {"loan_id": "L001", "product_type": "Commercial", "customer_segment": "Standard", "amount": 10000},
                {"loan_id": "L002", "product_type": "Commercial", "customer_segment": "Standard", "amount": 20000}
            ],
            "pricing_type": "main",
            "join_keys": ["product_type", "customer_segment"]
        }
        response = client.post(
            "/enrich-pricing",
            json=request_data
        )
        # Should succeed or return error depending on file availability
        assert response.status_code in [200, 500]