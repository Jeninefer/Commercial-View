"""Comprehensive KPI Calculator for Commercial View."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class KPIConfig:
    """Configuration for KPI calculations."""
    
    metric_name: str
    target_value: float
    weight: float = 1.0
    threshold: Optional[float] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.weight < 0:
            raise ValueError("Weight must be non-negative")
        if self.threshold is not None and self.threshold < 0:
            raise ValueError("Threshold must be non-negative")


class ComprehensiveKPICalculator:
    """Calculator for comprehensive KPI metrics."""
    
    def __init__(self, configs: list[KPIConfig] = None):
        """Initialize the KPI calculator with optional configurations.
        
        Args:
            configs: List of KPI configurations
        """
        self.configs = configs or []
        self._metrics: Dict[str, float] = {}
    
    def add_config(self, config: KPIConfig) -> None:
        """Add a KPI configuration.
        
        Args:
            config: KPI configuration to add
        """
        self.configs.append(config)
    
    def calculate_kpi(self, metric_data: Dict[str, float]) -> Dict[str, Any]:
        """Calculate KPIs based on metric data.
        
        Args:
            metric_data: Dictionary of metric names to values
            
        Returns:
            Dictionary containing calculated KPIs and their status
        """
        results = {}
        
        for config in self.configs:
            if config.metric_name in metric_data:
                value = metric_data[config.metric_name]
                achievement = (value / config.target_value) * 100 if config.target_value != 0 else 0
                
                status = "on_track"
                if config.threshold is not None:
                    status = "at_risk" if achievement < config.threshold else "on_track"
                
                results[config.metric_name] = {
                    "value": value,
                    "target": config.target_value,
                    "achievement_percent": achievement,
                    "status": status,
                    "weight": config.weight
                }
        
        return results
    
    def get_overall_score(self, metric_data: Dict[str, float]) -> float:
        """Calculate weighted overall KPI score.
        
        Args:
            metric_data: Dictionary of metric names to values
            
        Returns:
            Weighted average achievement percentage
        """
        results = self.calculate_kpi(metric_data)
        
        if not results:
            return 0.0
        
        total_weight = sum(config.weight for config in self.configs)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            results[config.metric_name]["achievement_percent"] * config.weight
            for config in self.configs
            if config.metric_name in results
        )
        
        return weighted_sum / total_weight


def create_sample_data() -> Dict[str, float]:
    """Create sample metric data for testing purposes.
    
    Returns:
        Dictionary of sample metric data
    """
    return {
        "revenue": 1000000.0,
        "customer_satisfaction": 85.0,
        "market_share": 15.5,
        "operational_efficiency": 92.0,
        "employee_retention": 88.5
    }
