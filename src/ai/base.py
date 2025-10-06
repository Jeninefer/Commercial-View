"""Base definitions for AI provider integrations."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional


class ProviderAuthenticationError(RuntimeError):
    """Raised when a provider cannot authenticate with the given credentials."""


class ProviderConfigurationError(RuntimeError):
    """Raised when a provider or service is misconfigured."""


@dataclass
class ProviderMetadata:
    """Metadata describing an AI provider."""

    name: str
    model: Optional[str] = None
    api_base: Optional[str] = None
    scopes: Optional[Iterable[str]] = None


class BaseAIClient(abc.ABC):
    """Abstract base client describing the required AI client interface."""

    metadata: ProviderMetadata

    def __init__(self, metadata: ProviderMetadata) -> None:
        self.metadata = metadata

    @abc.abstractmethod
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """Generate natural language given an input prompt."""

    @abc.abstractmethod
    def structured_predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return a structured prediction based on the supplied payload."""

    @abc.abstractmethod
    def healthcheck(self) -> Dict[str, Any]:
        """Return metadata proving the client is ready for traffic."""
