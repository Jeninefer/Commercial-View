"""FastAPI entrypoint exposing Commercial View analytics endpoints."""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field, validator

from .ai.schemas import AnomalyDetectionResult, ExecutiveSummary, PredictionResult
from .ai.services import (
    AIServiceContainer,
    AnomalyDetectionService,
    ExecutiveSummaryService,
    PredictionService,
)

app = FastAPI(title="Commercial View API")


def get_ai_container() -> AIServiceContainer:
    """Instantiate the AI service container lazily."""

    if not hasattr(get_ai_container, "_instance"):
        get_ai_container._instance = AIServiceContainer.from_env()
    return get_ai_container._instance  # type: ignore[attr-defined]


class ForecastRequest(BaseModel):
    """Request payload for forecasting analytics."""

    history: List[float] = Field(..., min_items=1, description="Historical KPI series")
    horizon: int = Field(default=3, gt=0, description="Number of future periods to forecast")

    @validator("history", each_item=True)
    def validate_history(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("History values must be numeric")
        return float(value)


class AnomalyRequest(BaseModel):
    """Request payload for anomaly detection."""

    series: List[float] = Field(..., min_items=3, description="Time-series values for evaluation")

    @validator("series", each_item=True)
    def validate_series(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise ValueError("Series values must be numeric")
        return float(value)


class ExecutiveSummaryRequest(BaseModel):
    """Request payload for executive summary generation."""

    metrics: Dict[str, float] = Field(..., description="KPI mapping used to craft the summary")
    sentiment: Optional[str] = Field(default=None, description="Optional tone override")

    @validator("metrics")
    def validate_metrics(cls, value: Dict[str, float]) -> Dict[str, float]:
        if not value:
            raise ValueError("At least one metric is required")
        for key, metric_value in value.items():
            if not isinstance(metric_value, (int, float)):
                raise ValueError(f"Metric '{key}' must be numeric")
        return {key: float(metric_value) for key, metric_value in value.items()}

    @validator("sentiment")
    def validate_sentiment(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value.lower() not in {"positive", "neutral", "negative"}:
            raise ValueError("Sentiment must be one of: positive, neutral, negative")
        return value.lower()


@app.post("/analytics/predictions", response_model=PredictionResult)
def generate_predictions(
    payload: ForecastRequest,
    container: AIServiceContainer = Depends(get_ai_container),
) -> PredictionResult:
    """Return AI narrated forecast results."""

    service = PredictionService(container)
    return service.forecast(history=payload.history, horizon=payload.horizon)


@app.post("/analytics/anomalies", response_model=AnomalyDetectionResult)
def detect_anomalies(
    payload: AnomalyRequest,
    container: AIServiceContainer = Depends(get_ai_container),
) -> AnomalyDetectionResult:
    """Detect anomalies in KPI series and narrate results."""

    service = AnomalyDetectionService(container)
    return service.detect(series=payload.series)


@app.post("/analytics/executive-summary", response_model=ExecutiveSummary)
def create_executive_summary(
    payload: ExecutiveSummaryRequest,
    container: AIServiceContainer = Depends(get_ai_container),
) -> ExecutiveSummary:
    """Generate an executive summary using AI providers."""

    service = ExecutiveSummaryService(container)
    return service.generate(metrics=payload.metrics, sentiment=payload.sentiment)


@app.get("/executive-summary", response_model=ExecutiveSummary)
def default_executive_summary(
    container: AIServiceContainer = Depends(get_ai_container),
) -> ExecutiveSummary:
    """Provide a default executive summary using baseline KPIs."""

    baseline_metrics = {
        "portfolio_value": 12_500_000.0,
        "delinquency_rate": 0.035,
        "net_interest_margin": 0.042,
    }
    service = ExecutiveSummaryService(container)
    try:
        return service.generate(metrics=baseline_metrics)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail=str(exc)) from exc
