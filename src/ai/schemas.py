"""Pydantic schemas for AI analytics responses."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionResult(BaseModel):
    """Structured output from the prediction service."""

    predictions: List[float] = Field(..., description="Point forecasts for future periods")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")
    narrative: str = Field(..., description="Executive-ready explanation of the forecast")
    provider: str = Field(..., description="Provider responsible for the narrative")


class AnomalyDetail(BaseModel):
    """Description of a detected anomaly."""

    index: int
    value: float
    severity: float = Field(..., ge=0, le=1)
    rationale: str


class AnomalyDetectionResult(BaseModel):
    """Structured output of anomaly detection."""

    anomalies: List[AnomalyDetail]
    provider: str
    summary: str


class ExecutiveSummary(BaseModel):
    """Narrative summary of portfolio performance."""

    title: str = Field(..., description="Short headline for the summary")
    narrative: str = Field(..., description="Detailed summary suitable for leadership briefings")
    highlights: Dict[str, str] = Field(default_factory=dict, description="Key KPI callouts")
    provider: str
    sentiment: Optional[str] = Field(default=None, description="Overall tone of the summary")
