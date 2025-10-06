"""AI integration package for Commercial View."""

from .base import (
    BaseAIClient,
    ProviderAuthenticationError,
    ProviderConfigurationError,
)
from .providers import (
    OpenAIClient,
    GeminiClient,
    AnthropicClient,
    HubSpotClient,
    ProviderRegistry,
)
from .schemas import (
    PredictionResult,
    AnomalyDetectionResult,
    ExecutiveSummary,
)
from .services import (
    AIServiceContainer,
    PredictionService,
    AnomalyDetectionService,
    ExecutiveSummaryService,
)

__all__ = [
    "AIServiceContainer",
    "AnomalyDetectionResult",
    "AnomalyDetectionService",
    "AnthropicClient",
    "BaseAIClient",
    "ExecutiveSummary",
    "ExecutiveSummaryService",
    "GeminiClient",
    "HubSpotClient",
    "OpenAIClient",
    "PredictionResult",
    "PredictionService",
    "ProviderAuthenticationError",
    "ProviderConfigurationError",
    "ProviderRegistry",
]
