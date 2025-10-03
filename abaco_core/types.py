"""
Type definitions for the KPI Calculator
"""

from typing import TypedDict


class Thresholds(TypedDict):
    """Thresholds for viability scoring"""
    runway_months_min: float
    ltv_cac_ratio_min: float
    nrr_min: float
