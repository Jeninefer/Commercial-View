"""
Commercial View - Comprehensive KPI Calculator

A comprehensive library for calculating loan portfolio KPIs.
"""

from .kpi_calculator import (
    KPIConfig,
    ComprehensiveKPICalculator,
    calculate_comprehensive_kpis,
    calculate_exposure_metrics,
    calculate_yield_metrics,
    calculate_delinquency_metrics,
    calculate_utilization_metrics,
    calculate_segment_mix_metrics,
    calculate_vintage_metrics,
)

__version__ = "0.1.0"

__all__ = [
    "KPIConfig",
    "ComprehensiveKPICalculator",
    "calculate_comprehensive_kpis",
    "calculate_exposure_metrics",
    "calculate_yield_metrics",
    "calculate_delinquency_metrics",
    "calculate_utilization_metrics",
    "calculate_segment_mix_metrics",
    "calculate_vintage_metrics",
]
