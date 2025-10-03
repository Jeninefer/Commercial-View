"""Startup Viability Analyzer

This module provides functionality to analyze startup viability based on key metrics.
"""

from typing import Dict


class StartupAnalyzer:
    """Analyzes startup viability based on key performance indicators."""
    
    def __init__(self, thresholds: Dict[str, float] = None):
        """Initialize the analyzer with thresholds.
        
        Args:
            thresholds: Dictionary containing minimum threshold values for:
                - runway_months_min: Minimum months of runway
                - ltv_cac_ratio_min: Minimum LTV/CAC ratio
                - nrr_min: Minimum net revenue retention (as decimal, e.g., 1.0 = 100%)
        """
        if thresholds is None:
            # Default thresholds
            self.thresholds = {
                "runway_months_min": 12,
                "ltv_cac_ratio_min": 3.0,
                "nrr_min": 1.0  # 1.0 = 100%
            }
        else:
            self.thresholds = thresholds
    
    def compute_viability_index(self, startup_metrics: Dict[str, float]) -> int:
        """Compute viability index for a startup based on its metrics.
        
        The index is computed as a weighted score (0-100) based on:
        - Runway (40%): Months of cash runway remaining
        - LTV/CAC (40%): Lifetime value to customer acquisition cost ratio
        - NRR (20%): Net revenue retention rate
        
        Args:
            startup_metrics: Dictionary containing startup metrics:
                - runway_months: Number of months of cash runway
                - ltv_cac_ratio or ltv_cac: LTV/CAC ratio
                - nrr: Net revenue retention (1.0 = 100%)
        
        Returns:
            Integer viability index score from 0 to 100
        """
        t = self.thresholds
        runway = float(startup_metrics.get("runway_months", 0) or 0)
        ltv_cac = float(startup_metrics.get("ltv_cac_ratio", startup_metrics.get("ltv_cac", 0)) or 0)
        nrr = float(startup_metrics.get("nrr", 0) or 0)  # assume 1.0 == 100%

        score = 0.0

        # Runway (40%)
        if runway >= 2*t["runway_months_min"]:
            s = 100
        elif runway >= t["runway_months_min"]:
            s = 75
        elif runway >= t["runway_months_min"]/2:
            s = 50
        elif runway > 0:
            s = 25
        else:
            s = 0
        score += 0.4 * s

        # LTV/CAC (40%)
        if ltv_cac >= 2*t["ltv_cac_ratio_min"]:
            s = 100
        elif ltv_cac >= t["ltv_cac_ratio_min"]:
            s = 75
        elif ltv_cac >= t["ltv_cac_ratio_min"]/2:
            s = 50
        elif ltv_cac > 0:
            s = 25
        else:
            s = 0
        score += 0.4 * s

        # NRR (20%) where 1.0 = threshold 100%
        if nrr >= 1.2 * t["nrr_min"]:
            s = 100
        elif nrr >= t["nrr_min"]:
            s = 75
        elif nrr >= 0.8 * t["nrr_min"]:
            s = 50
        elif nrr > 0:
            s = 25
        else:
            s = 0
        score += 0.2 * s

        return int(round(score))
