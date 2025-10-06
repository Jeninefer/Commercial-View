"""API endpoint contract tests for the FastAPI service layer."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_executive_summary_endpoint_returns_expected_structure() -> None:
    response = client.get("/executive-summary")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"portfolio_overview", "risk_indicators"}


def test_executive_summary_endpoint_uses_http_get_only() -> None:
    response = client.post("/executive-summary")
    assert response.status_code == 405
