"""Analysis package for Commercial View Platform."""

from .kpi_calculator import KPICalculator, calculate_portfolio_kpis

# Optional AI imports (require API keys and packages)
try:
    from .ai_analyzer import AIAnalyzer, analyze_data, LLMProvider
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AIAnalyzer = None
    analyze_data = None
    LLMProvider = None

__all__ = [
    'AIAnalyzer',
    'analyze_data',
    'LLMProvider',
    'KPICalculator',
    'calculate_portfolio_kpis',
    'AI_AVAILABLE',
]
