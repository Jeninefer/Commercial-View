"""Hybrid AI orchestration module for Commercial-View.

This module coordinates AI providers (Gemini, OpenAI, and an on-platform
fallback generator) to deliver context-aware narratives for different
stakeholder views. Gemini is used by default for executive summaries while
OpenAI powers investor-facing and deep analytics commentary. A resilient
fallback chain guarantees deterministic output even when third-party
providers are unavailable.
"""

from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

logger = logging.getLogger(__name__)


class AIProviderError(RuntimeError):
    """Raised when an AI provider cannot fulfill a request."""


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate content from the provider."""


class GeminiProvider(AIProvider):
    """Gemini provider wrapper with graceful degradation."""

    def __init__(self, model: str = "gemini-1.5-pro-latest") -> None:
        super().__init__("gemini")
        self._model_name = model
        self._client = None
        self._available = False
        self._initialize_client()

    def _initialize_client(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("Gemini provider disabled – GEMINI_API_KEY missing")
            return
        try:
            import google.generativeai as genai  # type: ignore

            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(self._model_name)
            self._available = True
            logger.info("Gemini provider initialized successfully")
        except ImportError:
            logger.warning(
                "google-generativeai package not installed – Gemini provider unavailable"
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"Failed to initialize Gemini provider: {exc}")

    def generate(self, prompt: str, **kwargs: Any) -> str:
        if not self._available or not self._client:
            raise AIProviderError("Gemini provider is not available")
        try:
            response = self._client.generate_content(prompt)
            # google-generativeai responses expose .text for aggregated output
            return getattr(response, "text", "").strip()
        except Exception as exc:  # pragma: no cover - upstream failure
            raise AIProviderError(f"Gemini generation failed: {exc}") from exc


class OpenAIProvider(AIProvider):
    """OpenAI provider wrapper with structured error handling."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        super().__init__("openai")
        self._model_name = model
        self._client = None
        self._available = False
        self._initialize_client()

    def _initialize_client(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI provider disabled – OPENAI_API_KEY missing")
            return
        try:
            from openai import OpenAI  # type: ignore

            self._client = OpenAI(api_key=api_key)
            self._available = True
            logger.info("OpenAI provider initialized successfully")
        except ImportError:
            logger.warning("openai package not installed – OpenAI provider unavailable")
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"Failed to initialize OpenAI provider: {exc}")

    def generate(self, prompt: str, **kwargs: Any) -> str:
        if not self._available or not self._client:
            raise AIProviderError("OpenAI provider is not available")
        try:
            completion = self._client.chat.completions.create(
                model=self._model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            output_text = ""
            if completion and hasattr(completion, "choices") and completion.choices:
                # Extract the generated message content from the first choice
                output_text = completion.choices[0].message.content
            return output_text.strip()
        except Exception as exc:  # pragma: no cover - upstream failure
            raise AIProviderError(f"OpenAI generation failed: {exc}") from exc


class LocalScribeProvider(AIProvider):
    """Deterministic fallback provider using handcrafted summarisation."""

    def __init__(self) -> None:
        super().__init__("local")

    def generate(self, prompt: str, **kwargs: Any) -> str:
        snapshot = kwargs.get("snapshot")
        bullets: Iterable[str] = []
        if isinstance(snapshot, dict):
            bullets = self._summarise_snapshot(snapshot)
        safe_prompt = prompt.splitlines()[0][:80] if prompt else "summary"
        summary_lines = [
            f"Automated narrative for {safe_prompt}:",
            "- Providers unavailable – using deterministic insights",
        ]
        summary_lines.extend(f"- {line}" for line in bullets)
        return "\n".join(summary_lines)

    def _summarise_snapshot(self, snapshot: Dict[str, Any]) -> Iterable[str]:
        portfolio = snapshot.get("portfolio", {})
        risk = snapshot.get("risk", {})
        alerts = snapshot.get("alerts", [])

        lines = []
        if portfolio:
            outstanding = portfolio.get("portfolio_outstanding")
            if outstanding is not None:
                lines.append(f"Portfolio outstanding: {outstanding:,.2f}")
            apr = portfolio.get("weighted_apr")
            if apr is not None:
                lines.append(f"Weighted APR: {apr:.2f}%")
        if risk:
            npl = risk.get("npl_ratio")
            if npl is not None:
                lines.append(f"NPL ratio: {npl:.2f}%")
        if alerts:
            lines.append(f"Operational alerts: {len(alerts)} active signals")
        return lines


@dataclass
class HybridAIResult:
    provider: str
    text: str
    fallback_used: bool = False


class HybridAIOrchestrator:
    """Coordinates AI providers with fallback logic for dashboard narratives."""

    def __init__(
        self,
        providers: Optional[Dict[str, AIProvider]] = None,
        default_summary_provider: str = "gemini",
        default_investor_provider: str = "openai",
        fallback_provider: str = "local",
    ) -> None:
        self.providers: Dict[str, AIProvider] = providers or {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "local": LocalScribeProvider(),
        }
        self.default_summary_provider = default_summary_provider
        self.default_investor_provider = default_investor_provider
        self.fallback_provider = fallback_provider

    def generate_summary(self, snapshot: Dict[str, Any]) -> HybridAIResult:
        """Generate an executive-ready summary using Gemini with fallback."""
        prompt = self._build_summary_prompt(snapshot)
        return self._generate_with_fallback(
            preferred=self.default_summary_provider,
            fallback=self.default_investor_provider,
            prompt=prompt,
            snapshot=snapshot,
        )

    def generate_investor_analysis(self, snapshot: Dict[str, Any]) -> HybridAIResult:
        """Generate investor-grade analysis preferring OpenAI."""
        prompt = self._build_investor_prompt(snapshot)
        return self._generate_with_fallback(
            preferred=self.default_investor_provider,
            fallback=self.default_summary_provider,
            prompt=prompt,
            snapshot=snapshot,
        )

    def generate_operational_brief(self, snapshot: Dict[str, Any]) -> HybridAIResult:
        """Produce an operational management brief (Gemini first)."""
        prompt = self._build_operational_prompt(snapshot)
        return self._generate_with_fallback(
            preferred=self.default_summary_provider,
            fallback=self.default_investor_provider,
            prompt=prompt,
            snapshot=snapshot,
        )

    def _generate_with_fallback(
        self,
        *,
        preferred: str,
        fallback: Optional[str],
        prompt: str,
        snapshot: Optional[Dict[str, Any]] = None,
    ) -> HybridAIResult:
        providers_to_try = [preferred]
        if fallback and fallback not in providers_to_try:
            providers_to_try.append(fallback)
        if self.fallback_provider not in providers_to_try:
            providers_to_try.append(self.fallback_provider)

        last_exception: Optional[Exception] = None
        for provider_name in providers_to_try:
            provider = self.providers.get(provider_name)
            if not provider:
                continue
            try:
                text = provider.generate(prompt, snapshot=snapshot)
                return HybridAIResult(
                    provider=provider_name,
                    text=text,
                    fallback_used=provider_name != preferred,
                )
            except Exception as exc:  # pragma: no cover - defensive
                last_exception = exc
                logger.warning(
                    "AI provider %s failed with error: %s", provider_name, exc
                )
                continue

        raise AIProviderError(
            f"All AI providers failed. Last error: {last_exception}"  # pragma: no cover
        )

    def _build_summary_prompt(self, snapshot: Dict[str, Any]) -> str:
        portfolio = snapshot.get("portfolio", {})
        risk = snapshot.get("risk", {})
        alerts = snapshot.get("alerts", [])
        return (
            "Craft a concise executive dashboard summary for the commercial lending "
            "portfolio. Focus on positive momentum and urgent watchouts. Here is the "
            "JSON payload you must analyse:\n"
            f"{json.dumps({'portfolio': portfolio, 'risk': risk, 'alerts': alerts}, default=str)}"
        )

    def _build_investor_prompt(self, snapshot: Dict[str, Any]) -> str:
        portfolio = snapshot.get("portfolio", {})
        growth = snapshot.get("growth", {})
        performance = snapshot.get("performance", {})
        return (
            "Prepare an investor-grade briefing emphasising growth, stability, and "
            "capital efficiency. Quantify runway, risk mitigation, and upside. Use "
            "this structured data:\n"
            f"{json.dumps({'portfolio': portfolio, 'growth': growth, 'performance': performance}, default=str)}"
        )

    def _build_operational_prompt(self, snapshot: Dict[str, Any]) -> str:
        ops = snapshot.get("operations", {})
        alerts = snapshot.get("alerts", [])
        risk = snapshot.get("risk", {})
        return (
            "Synthesize an operations huddle brief. Highlight critical alerts, DPD "
            "pressure points, and immediate actions for collections and servicing. "
            "Context payload:\n"
            f"{json.dumps({'operations': ops, 'alerts': alerts, 'risk': risk}, default=str)}"
        )


__all__ = [
    "AIProvider",
    "AIProviderError",
    "GeminiProvider",
    "OpenAIProvider",
    "LocalScribeProvider",
    "HybridAIOrchestrator",
    "HybridAIResult",
]
