"""Service layer orchestrating AI provider usage."""

from __future__ import annotations

import math
import statistics
from typing import Dict, Iterable, List, Optional

from .base import BaseAIClient, ProviderConfigurationError
from .providers import LocalEchoClient, ProviderRegistry
from .schemas import AnomalyDetectionResult, AnomalyDetail, ExecutiveSummary, PredictionResult


class AIServiceContainer:
    """Dependency container bundling configured AI provider clients."""

    provider_priority: Iterable[str] = ("openai", "anthropic", "gemini", "hubspot")

    def __init__(
        self,
        clients: Dict[str, BaseAIClient],
        fallback_client: Optional[BaseAIClient] = None,
    ) -> None:
        self._clients = dict(clients)
        self._fallback_client = fallback_client
        if not self._clients and self._fallback_client is None:
            raise ProviderConfigurationError(
                "AIServiceContainer requires at least one configured client or a fallback client."
            )

    @classmethod
    def from_env(cls, *, allow_fallback: bool = True) -> "AIServiceContainer":
        clients = ProviderRegistry.configured_clients(allow_empty=True)
        fallback: Optional[BaseAIClient] = None
        if not clients and allow_fallback:
            fallback = LocalEchoClient()
        return cls(clients=clients, fallback_client=fallback)

    @property
    def clients(self) -> Dict[str, BaseAIClient]:
        return dict(self._clients)

    def is_configured(self, provider: str) -> bool:
        return provider in self._clients

    def get_client(self, provider: Optional[str] = None) -> BaseAIClient:
        if provider:
            try:
                return self._clients[provider]
            except KeyError as exc:  # pragma: no cover - defensive branch
                raise ProviderConfigurationError(f"Provider '{provider}' is not configured") from exc
        for preferred in self.provider_priority:
            if preferred in self._clients:
                return self._clients[preferred]
        if self._clients:
            return next(iter(self._clients.values()))
        if self._fallback_client is not None:
            return self._fallback_client
        raise ProviderConfigurationError("No AI clients are available")

    def healthcheck(self) -> Dict[str, Dict[str, str]]:
        report: Dict[str, Dict[str, str]] = {}
        for name, client in self._clients.items():
            report[name] = client.healthcheck()
        if self._fallback_client is not None:
            report[self._fallback_client.metadata.name] = self._fallback_client.healthcheck()
        return report


class PredictionService:
    """Forecasting utilities backed by AI narrative generation."""

    def __init__(self, container: AIServiceContainer) -> None:
        self._container = container

    def forecast(self, history: List[float], horizon: int = 3) -> PredictionResult:
        if not history:
            raise ValueError("Historical data is required for forecasting")
        if horizon <= 0:
            raise ValueError("Horizon must be a positive integer")

        trailing = history[-min(len(history), 6):]
        mean = statistics.mean(trailing)
        if len(trailing) > 1:
            deltas = [b - a for a, b in zip(trailing[:-1], trailing[1:])]
            avg_delta = statistics.mean(deltas)
        else:
            avg_delta = 0.0

        predictions = [round(trailing[-1] + avg_delta * (idx + 1), 2) for idx in range(horizon)]
        variance = statistics.pvariance(trailing) if len(trailing) > 1 else 0.0
        volatility = math.sqrt(max(variance, 0))
        confidence = max(0.1, min(0.95, 1.0 - volatility / (abs(mean) + 1e-6)))

        prompt = (
            "Summarize the forecast for a financial portfolio. Provide insight into drivers and risk. "
            f"Historical points: {trailing}. Forecast horizon: {horizon} periods."
        )
        client = self._container.get_client()
        narrative = client.generate_text(prompt)

        return PredictionResult(
            predictions=predictions,
            confidence=round(confidence, 2),
            narrative=narrative,
            provider=client.metadata.name,
        )


class AnomalyDetectionService:
    """Detect anomalies in time-series data and narrate findings."""

    def __init__(self, container: AIServiceContainer, threshold: float = 2.0) -> None:
        self._container = container
        self._threshold = threshold

    def detect(self, series: List[float]) -> AnomalyDetectionResult:
        if not series:
            raise ValueError("Series is required for anomaly detection")
        if len(series) < 3:
            raise ValueError("Series must contain at least three observations")

        mean = statistics.mean(series)
        std_dev = statistics.pstdev(series)
        anomalies: List[AnomalyDetail] = []
        if std_dev == 0:
            std_dev = 1e-6
        for idx, value in enumerate(series):
            z_score = abs((value - mean) / std_dev)
            if z_score >= self._threshold:
                severity = min(1.0, z_score / (self._threshold * 2))
                rationale = f"Z-score {z_score:.2f} exceeds threshold {self._threshold:.2f}"
                anomalies.append(
                    AnomalyDetail(index=idx, value=value, severity=round(severity, 2), rationale=rationale)
                )

        client = self._container.get_client()
        prompt = (
            "Explain anomalies in the supplied financial metrics. Highlight operational insights. "
            f"Series: {series}. Detected anomalies: {len(anomalies)}."
        )
        summary = client.generate_text(prompt)

        return AnomalyDetectionResult(anomalies=anomalies, provider=client.metadata.name, summary=summary)


class ExecutiveSummaryService:
    """Craft executive-ready summaries grounded in KPI metrics."""

    def __init__(self, container: AIServiceContainer) -> None:
        self._container = container

    def generate(self, metrics: Dict[str, float], *, sentiment: Optional[str] = None) -> ExecutiveSummary:
        if not metrics:
            raise ValueError("Metrics payload cannot be empty")

        client = self._container.get_client()
        highlights = {
            metric.replace("_", " ").title(): f"{value:,.2f}"
            for metric, value in metrics.items()
        }
        prompt = (
            "Craft a concise executive summary for a lending analytics dashboard. "
            "Reference the following metrics and provide actions: "
            f"{metrics}."
        )
        narrative = client.generate_text(prompt)
        title = f"Portfolio outlook powered by {client.metadata.name.title()}"
        derived_sentiment = sentiment or ("positive" if statistics.mean(metrics.values()) >= 0 else "neutral")

        return ExecutiveSummary(
            title=title,
            narrative=narrative,
            highlights=highlights,
            provider=client.metadata.name,
            sentiment=derived_sentiment,
        )
