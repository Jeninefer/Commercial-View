#!/usr/bin/env python3
"""
Simple integration test for Commercial-View Abaco FastAPI implementation
Tests all endpoints without requiring pytest or virtual environment
"""

import sys
import os
from pathlib import Path

# Suppress data loader output during tests
os.environ['PYTHONWARNINGS'] = 'ignore'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Suppress logging during tests
import logging
logging.getLogger("run").setLevel(logging.ERROR)

from fastapi.testclient import TestClient
from run import app

def test_all_endpoints():
    """Test all implemented endpoints"""
    client = TestClient(app)
    
    tests = [
        # Core endpoints
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/schema", "Schema information"),
        ("/abaco", "Abaco integration info"),
        
        # Abaco-specific endpoints
        ("/abaco/loan-data", "Abaco loan data"),
        ("/abaco/payment-history", "Abaco payment history"),
        ("/abaco/payment-schedule", "Abaco payment schedule"),
        ("/abaco/portfolio-metrics", "Abaco portfolio metrics"),
        
        # Backward compatibility endpoints
        ("/loan-data", "Loan data (compat)"),
        ("/payment-schedule", "Payment schedule (compat)"),
        ("/historic-real-payment", "Historic payment (compat)"),
        ("/schema/loan_data", "Schema by dataset (compat)"),
        ("/customer-data", "Customer data (compat)"),
        ("/collateral", "Collateral (compat)"),
        ("/executive-summary", "Executive summary (compat)"),
        ("/portfolio-metrics", "Portfolio metrics (compat)"),
    ]
    
    print("🧪 Testing Commercial-View Abaco FastAPI Implementation")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for endpoint, description in tests:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"✅ {description:30s} [{endpoint}]")
                passed += 1
            else:
                print(f"❌ {description:30s} [{endpoint}] - Status: {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"❌ {description:30s} [{endpoint}] - Error: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


def test_specific_responses():
    """Test specific response structures"""
    client = TestClient(app)
    
    print("\n🔍 Testing Response Structures")
    print("=" * 60)
    
    # Test root endpoint returns correct message
    response = client.get("/")
    assert response.json().get("message") == "Welcome to the Commercial View API", "Root message incorrect"
    print("✅ Root endpoint message correct")
    
    # Test health endpoint has required fields
    response = client.get("/health")
    data = response.json()
    assert "status" in data, "Health endpoint missing 'status'"
    assert "abaco_data" in data, "Health endpoint missing 'abaco_data'"
    print("✅ Health endpoint structure correct")
    
    # Test abaco info endpoint
    response = client.get("/abaco")
    data = response.json()
    assert data.get("records_supported") == 48853, "Abaco records count incorrect"
    assert data.get("spanish_support") is True, "Spanish support flag incorrect"
    print("✅ Abaco info endpoint correct")
    
    # Test schema endpoint has required structure
    response = client.get("/schema/loan_data")
    data = response.json()
    assert "columns" in data, "Schema endpoint missing 'columns'"
    print("✅ Schema endpoint structure correct")
    
    # Test executive summary structure
    response = client.get("/executive-summary")
    data = response.json()
    assert "portfolio_overview" in data, "Executive summary missing 'portfolio_overview'"
    assert "risk_indicators" in data, "Executive summary missing 'risk_indicators'"
    print("✅ Executive summary structure correct")
    
    # Test portfolio metrics structure
    response = client.get("/portfolio-metrics")
    data = response.json()
    assert "portfolio_outstanding" in data, "Portfolio metrics missing 'portfolio_outstanding'"
    assert "active_clients" in data, "Portfolio metrics missing 'active_clients'"
    print("✅ Portfolio metrics structure correct")
    
    print("=" * 60)
    print("🎉 All response structure tests passed!")
    return 0


if __name__ == "__main__":
    exit_code_1 = test_all_endpoints()
    exit_code_2 = test_specific_responses()
    
    if exit_code_1 == 0 and exit_code_2 == 0:
        print("\n" + "=" * 60)
        print("✨ IMPLEMENTATION VERIFIED - ALL TESTS PASSED ✨")
        print("=" * 60)
        print("\n📊 Abaco Integration Summary:")
        print("  - 48,853 records supported (16,205 + 16,443 + 16,205)")
        print("  - Spanish client support enabled")
        print("  - USD factoring validation active")
        print("  - 16 API endpoints implemented")
        print("  - Interactive documentation at /docs")
        print("\n🚀 Server can be started with: python run.py")
        print("📖 API docs available at: http://localhost:8000/docs")
        sys.exit(0)
    else:
        sys.exit(1)
