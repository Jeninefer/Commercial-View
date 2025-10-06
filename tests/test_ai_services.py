"""Unit tests for AI-powered analytics services."""

from __future__ import annotations

import math
from typing import List

import pytest
from fastapi.testclient import TestClient

from src.ai.providers import LocalEchoClient
from src.ai.schemas import AnomalyDetectionResult, ExecutiveSummary, PredictionResult
from src.ai.services import (
    AIServiceContainer,
    AnomalyDetectionService,
    ExecutiveSummaryService,
    PredictionService,
)
from src.api import app, get_ai_container


class StubClient(LocalEchoClient):
    """Deterministic client that tracks prompts for assertions."""

    def __init__(self) -> None:
        super().__init__(name="stub-provider")
        self.prompts: List[str] = []

    def generate_text(self, prompt: str, **kwargs) -> str:  # type: ignore[override]
        self.prompts.append(prompt)
        return "stub narrative"


@pytest.fixture()
def stub_container() -> AIServiceContainer:
    client = StubClient()
    return AIServiceContainer(clients={client.metadata.name: client})


def test_prediction_service_returns_forecast(stub_container: AIServiceContainer) -> None:
    service = PredictionService(stub_container)
    result = service.forecast(history=[10, 12, 15, 14], horizon=2)
    assert isinstance(result, PredictionResult)
    assert result.predictions == [13.0, 12.0]
    assert math.isclose(result.confidence, 0.95, rel_tol=1e-6) is False
    assert result.provider == "stub-provider"


def test_anomaly_detection_service_flags_outliers(stub_container: AIServiceContainer) -> None:
    service = AnomalyDetectionService(stub_container, threshold=1.0)
    result = service.detect(series=[10, 11, 50, 12, 9])
    assert isinstance(result, AnomalyDetectionResult)
    assert any(anomaly.index == 2 for anomaly in result.anomalies)
    assert result.provider == "stub-provider"


def test_executive_summary_provides_highlights(stub_container: AIServiceContainer) -> None:
    service = ExecutiveSummaryService(stub_container)
    metrics = {"net_income": 1500000.0, "charge_off_rate": -0.02}
    result = service.generate(metrics=metrics, sentiment="positive")
    assert isinstance(result, ExecutiveSummary)
    assert "Net Income" in result.highlights
    assert result.sentiment == "positive"


def test_api_endpoints_use_ai_services(monkeypatch: pytest.MonkeyPatch) -> None:
    client = StubClient()
    container = AIServiceContainer(clients={client.metadata.name: client})
    monkeypatch.setattr(get_ai_container, "_instance", container, raising=False)

    test_client = TestClient(app)

    forecast_response = test_client.post(
        "/analytics/predictions",
        json={"history": [1, 2, 3], "horizon": 2},
    )
    assert forecast_response.status_code == 200
    assert forecast_response.json()["provider"] == "stub-provider"

    anomaly_response = test_client.post(
        "/analytics/anomalies",
        json={"series": [1, 2, 10, 2, 1]},
    )
    assert anomaly_response.status_code == 200
    assert anomaly_response.json()["provider"] == "stub-provider"

    summary_response = test_client.post(
        "/analytics/executive-summary",
        json={"metrics": {"roi": 0.12}},
    )
    assert summary_response.status_code == 200
    assert summary_response.json()["provider"] == "stub-provider"
