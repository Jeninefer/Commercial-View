"""
Metrics registry module extracted from PR #9
Performance monitoring and data quality tracking
"""

from typing import Dict, List, Any
from datetime import datetime
import numpy as np


class MetricsRegistry:
    """Registry for tracking performance and data quality metrics"""

    def __init__(self):
        self.metrics = {}
        self.performance_logs = []
        self.data_quality_checks = {}

    def track_performance(self, operation: str, duration: float):
        """Track operation performance"""
        self.performance_logs.append(
            {
                "operation": operation,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def register_metric(self, name: str, value: Any, category: str = "general"):
        """Register a metric value"""
        if category not in self.metrics:
            self.metrics[category] = {}

        self.metrics[category][name] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }

    def check_data_quality(self, data_frame, checks: List[str]) -> Dict[str, bool]:
        """Run data quality checks"""
        quality_results = {}

        for check in checks:
            if check == "no_nulls":
                quality_results[check] = not data_frame.isnull().any().any()
            elif check == "positive_values":
                numeric_cols = data_frame.select_dtypes(include=[np.number]).columns
                quality_results[check] = (data_frame[numeric_cols] >= 0).all().all()
            # ...existing code for other quality checks...

        self.data_quality_checks[datetime.now().isoformat()] = quality_results
        return quality_results

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        if not self.performance_logs:
            return {"average_duration": 0, "operation_count": 0}

        durations = [log["duration"] for log in self.performance_logs]
        return {
            "average_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "operation_count": len(self.performance_logs),
        }
