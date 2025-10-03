"""KPI Configuration classes"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class KPIConfig:
    """
    Configuration for KPI calculations.
    """
    # Risk thresholds
    risk_threshold_high: float = 0.7
    risk_threshold_medium: float = 0.4
    
    # Default values
    default_interest_rate: float = 0.05
    default_ltv_ratio: float = 0.8
    
    # Calculation parameters
    enable_advanced_metrics: bool = True
    enable_validation: bool = True
    
    # Additional configuration
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.risk_threshold_high < self.risk_threshold_medium:
            raise ValueError(
                f"risk_threshold_high ({self.risk_threshold_high}) must be >= "
                f"risk_threshold_medium ({self.risk_threshold_medium})"
            )
        if not 0 <= self.default_ltv_ratio <= 1:
            raise ValueError(
                f"default_ltv_ratio must be between 0 and 1, got {self.default_ltv_ratio}"
            )
