"""Provider implementations for Commercial View AI integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from .base import (
    BaseAIClient,
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderMetadata,
)

_SIMULATED_LATENCY_MS = 40


@dataclass
class _SimulatedResponse:
    """Utility container returned by simulated client calls."""

    content: str
    latency_ms: int = _SIMULATED_LATENCY_MS
    provider: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "latency_ms": self.latency_ms,
            "provider": self.provider,
        }


class _BaseConfiguredClient(BaseAIClient):
    """Base class implementing shared configuration validation."""

    required_env_vars: Iterable[str] = ()

    def __init__(
        self,
        metadata: ProviderMetadata,
        required_env_vars: Optional[Iterable[str]] = None,
    ) -> None:
        required = required_env_vars if required_env_vars is not None else self.required_env_vars
        missing: List[str] = [var for var in required if not os.getenv(var)]
        if missing:
            raise ProviderAuthenticationError(
                f"Missing required environment variables for {metadata.name}: {', '.join(missing)}"
            )
        super().__init__(metadata)

    def _simulate_completion(self, prompt: str, *, action: str) -> _SimulatedResponse:
        summary = prompt.strip().splitlines()[0][:120]
        content = (
            f"[{self.metadata.name}] {action} -> "
            f"{summary if summary else 'No prompt provided.'}"
        )
        return _SimulatedResponse(content=content, provider=self.metadata.name)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        return self._simulate_completion(prompt, action="text").content

    def structured_predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "provider": self.metadata.name,
            "model": self.metadata.model,
            "echo": payload,
        }

    def healthcheck(self) -> Dict[str, Any]:
        return {
            "provider": self.metadata.name,
            "model": self.metadata.model,
            "status": "ready",
        }


class OpenAIClient(_BaseConfiguredClient):
    """OpenAI provider implementation."""

    required_env_vars = ("OPENAI_API_KEY",)

    def __init__(self, model: Optional[str] = None) -> None:
        metadata = ProviderMetadata(
            name="openai",
            model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_base=os.getenv("OPENAI_BASE_URL"),
        )
        super().__init__(metadata)


class GeminiClient(_BaseConfiguredClient):
    """Google Gemini provider implementation."""

    required_env_vars = ("GEMINI_API_KEY",)

    def __init__(self, model: Optional[str] = None) -> None:
        metadata = ProviderMetadata(
            name="gemini",
            model=model or os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            api_base=os.getenv("GEMINI_API_BASE"),
        )
        super().__init__(metadata)


class AnthropicClient(_BaseConfiguredClient):
    """Anthropic provider implementation."""

    required_env_vars = ("ANTHROPIC_API_KEY",)

    def __init__(self, model: Optional[str] = None) -> None:
        metadata = ProviderMetadata(
            name="anthropic",
            model=model or os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            api_base=os.getenv("ANTHROPIC_API_BASE"),
        )
        super().__init__(metadata)


class HubSpotClient(_BaseConfiguredClient):
    """HubSpot data enrichment client."""

    required_env_vars = ("HUBSPOT_PRIVATE_APP_TOKEN",)

    def __init__(self, scope: Optional[str] = None) -> None:
        metadata = ProviderMetadata(
            name="hubspot",
            api_base=os.getenv("HUBSPOT_API_BASE", "https://api.hubapi.com"),
            scopes=(scope,) if scope else ("crm.objects.contacts.read", "crm.schemas.contacts.read"),
        )
        super().__init__(metadata)

    def structured_predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        base = super().structured_predict(payload)
        base.update({
            "description": "HubSpot structured enrichment",
        })
        return base


class ProviderRegistry:
    """Factory responsible for instantiating configured providers."""

    providers = (
        OpenAIClient,
        GeminiClient,
        AnthropicClient,
        HubSpotClient,
    )

    @classmethod
    def configured_clients(cls, *, allow_empty: bool = False) -> Dict[str, BaseAIClient]:
        clients: Dict[str, BaseAIClient] = {}
        for provider_cls in cls.providers:
            try:
                client = provider_cls()
            except ProviderAuthenticationError:
                continue
            clients[client.metadata.name] = client
        if not clients and not allow_empty:
            raise ProviderConfigurationError(
                "No AI providers are configured. Ensure required environment variables are set."
            )
        return clients


class LocalEchoClient(BaseAIClient):
    """Fallback client that operates without external dependencies."""

    def __init__(self, name: str = "local-echo") -> None:
        super().__init__(ProviderMetadata(name=name, model="heuristic"))

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        return f"[{self.metadata.name}] {prompt.strip()[:160]}"

    def structured_predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "provider": self.metadata.name,
            "prediction": payload,
        }

    def healthcheck(self) -> Dict[str, Any]:
        return {
            "provider": self.metadata.name,
            "status": "ready",
        }
