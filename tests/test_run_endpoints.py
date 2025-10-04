from __future__ import annotations

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import run as run_module

from run import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _loan_dataframe() -> pd.DataFrame:
    loan_row = {
        "Company": "Acme",
        "CustomerID": "CUST-001",
        "Cliente": "Acme Corp",
        "Pagador": "Acme Corp",
        "ApplicationID": "APP-001",
        "LoanID": "LN-001",
        "ProductType": "Term Loan",
        "DisbursementDate": "2023-01-01",
        "TPV": 1000.0,
        "DisbursementAmount": 1000.0,
        "OriginationFee": 10.0,
        "OriginationFeeTaxes": 1.2,
        "LoanCurrency": "USD",
        "InterestRateAPR": 0.05,
        "Term": 12,
        "TermUnit": "months",
        "PaymentFrequency": "monthly",
        "DaysInDefault": 0,
        "PledgeTo": None,
        "PledgeDate": None,
        "LoanStatus": "Active",
        "OutstandingLoanValue": 900.0,
        "Other": None,
        "NewLoanID": None,
        "NewLoanDate": None,
        "OldLoanID": None,
        "RecoveryDate": None,
        "RecoveryValue": None,
    }
    return pd.DataFrame([loan_row])


def _historic_dataframe() -> pd.DataFrame:
    historic_row = {
        "Company": "Acme",
        "CustomerID": "CUST-001",
        "Cliente": "Acme Corp",
        "Pagador": "Acme Corp",
        "LoanID": "LN-001",
        "TruePaymentDate": "2023-02-01",
        "TrueDevolution": 100.0,
        "TrueTotalPayment": 110.0,
        "TruePaymentCurrency": "USD",
        "TruePrincipalPayment": 100.0,
        "TrueInterestPayment": 10.0,
        "TrueFeePayment": 0.0,
        "TrueOtherPayment": pd.NA,
        "TrueTaxPayment": 0.0,
        "TrueFeeTaxPayment": 0.0,
        "TrueRebates": 0,
        "TrueOutstandingLoanValue": 800.0,
        "TruePaymentStatus": "paid",
    }
    return pd.DataFrame([historic_row])


def _schedule_dataframe() -> pd.DataFrame:
    schedule_row = {
        "Company": "Acme",
        "CustomerID": "CUST-001",
        "Cliente": "Acme Corp",
        "Pagador": "Acme Corp",
        "LoanID": "LN-001",
        "PaymentDate": "2023-03-01",
        "TPV": 1000.0,
        "TotalPayment": 110.0,
        "Currency": "USD",
        "PrincipalPayment": 100.0,
        "InterestPayment": 10.0,
        "FeePayment": 0.0,
        "OtherPayment": None,
        "TaxPayment": 0.0,
        "AllRebates": None,
        "OutstandingLoanValue": 700,
    }
    return pd.DataFrame([schedule_row])


def _customer_dataframe() -> pd.DataFrame:
    customer_row = {
        "business_year_founded": 1999,
        "equifax_score": "A",
        "category": "SMB",
        "credit_line_category": "Standard",
        "subcategory": "Retail",
        "credit_line_subcategory": "Consumer",
        "industry": "Retail",
        "birth_year": 1980,
        "occupation": "Owner",
        "client_type": "Business",
        "location_city": "New York",
        "location_state_province": "NY",
        "location_country": "USA",
        "customer_id": "CUST-001",
        "customer_name": "Acme Corp",
    }
    return pd.DataFrame([customer_row])


def _collateral_dataframe() -> pd.DataFrame:
    collateral_row = {
        "customer_id": "CUST-001",
        "customer_name": "Acme Corp",
        "loan_id": "LN-001",
        "collateral_id": "COL-001",
        "collateral_original_value": 1500.0,
        "collateral_current_value": 1400.0,
    }
    return pd.DataFrame([collateral_row])


def test_get_loan_data_serializes_to_models(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run_module, "load_loan_data", _loan_dataframe)

    response = client.get("/loan-data")

    assert response.status_code == 200
    payload = response.json()
    assert payload == [
        {
            "Company": "Acme",
            "CustomerID": "CUST-001",
            "Cliente": "Acme Corp",
            "Pagador": "Acme Corp",
            "ApplicationID": "APP-001",
            "LoanID": "LN-001",
            "ProductType": "Term Loan",
            "DisbursementDate": "2023-01-01",
            "TPV": 1000.0,
            "DisbursementAmount": 1000.0,
            "OriginationFee": 10.0,
            "OriginationFeeTaxes": 1.2,
            "LoanCurrency": "USD",
            "InterestRateAPR": 0.05,
            "Term": 12,
            "TermUnit": "months",
            "PaymentFrequency": "monthly",
            "DaysInDefault": 0,
            "PledgeTo": None,
            "PledgeDate": None,
            "LoanStatus": "Active",
            "OutstandingLoanValue": 900.0,
            "Other": None,
            "NewLoanID": None,
            "NewLoanDate": None,
            "OldLoanID": None,
            "RecoveryDate": None,
            "RecoveryValue": None,
        }
    ]


@pytest.mark.parametrize(
    "endpoint, loader_name, factory",
    [
        ("/historic-real-payment", "load_historic_real_payment", _historic_dataframe),
        ("/payment-schedule", "load_payment_schedule", _schedule_dataframe),
        ("/customer-data", "load_customer_data", _customer_dataframe),
        ("/collateral", "load_collateral", _collateral_dataframe),
    ],
)
def test_endpoints_return_serializable_payload(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    endpoint: str,
    loader_name: str,
    factory,
) -> None:
    monkeypatch.setattr(run_module, loader_name, factory)

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload, "Expected at least one record in the payload"
    assert payload[0][list(payload[0].keys())[0]] is not None


def test_missing_file_returns_not_found(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    assert any(v is not None for v in payload[0].values()), "Expected at least one non-None value in the first record"

def test_missing_file_returns_not_found(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    raise FileNotFoundError("missing file")
    response = client.get("/collateral")

    assert response.status_code == 404
    assert response.json()["detail"].startswith("Collateral data file not found")
