import importlib
import sys
import types
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
sys.modules.setdefault("requests", types.SimpleNamespace(get=None))

from src.data_loader import PRICING_FILENAMES
from src.models import LoanData


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    pricing_dir = tmp_path_factory.mktemp("pricing")

    loan_record = LoanData(
        Company="Test Company",
        CustomerID="CUST-001",
        Cliente="Acme Corp",
        Pagador="Acme Corp",
        ApplicationID="APP-001",
        LoanID="LN-001",
        ProductType="Term Loan",
        DisbursementDate=date(2024, 1, 1),
        TPV=100000.0,
        DisbursementAmount=100000.0,
        OriginationFee=1000.0,
        OriginationFeeTaxes=180.0,
        LoanCurrency="USD",
        InterestRateAPR=5.5,
        Term=12,
        TermUnit="Months",
        PaymentFrequency="Monthly",
        DaysInDefault=0,
        LoanStatus="Active",
        OutstandingLoanValue=90000.0,
    )

    loan_df = pd.DataFrame([loan_record.model_dump() if hasattr(loan_record, "model_dump") else loan_record.dict()])
    loan_df.to_csv(pricing_dir / PRICING_FILENAMES["loan_data"], index=False)

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("COMMERCIAL_VIEW_PRICING_PATH", str(pricing_dir))

    if "run" in sys.modules:
        app_module = importlib.reload(sys.modules["run"])
    else:
        app_module = importlib.import_module("run")

    yield app_module.app
    monkeypatch.undo()


@pytest.fixture(scope="module")
def client(app):
    return TestClient(app)


def _loan_data_fields():
    try:
        return set(LoanData.model_fields.keys())  # Pydantic v2
    except AttributeError:  # pragma: no cover - fallback for Pydantic v1
        return set(LoanData.__fields__.keys())


def test_get_loan_data_returns_serialisable_records(client):
    response = client.get("/loan-data")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert payload, "Expected loan data payload to be non-empty"

    record = payload[0]
    assert isinstance(record, dict)

    expected_fields = _loan_data_fields()
    assert set(record.keys()) == expected_fields

    assert isinstance(record["Company"], str)
    assert record["Company"], "Company field should not be empty"
