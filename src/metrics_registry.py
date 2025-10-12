"""
Metrics Registry Module for Commercial View
Centralized metrics collection and management
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsRegistry:
    """Central registry for metrics collection and management"""

    def __init__(self):
        self.metrics = {}
        self.logger = logger
        self.created_at = datetime.now()

    def register_metric(
        self, name: str, value: Any, metadata: Optional[Dict] = None
    ) -> None:
        """Register a new metric"""
        self.metrics[name] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.logger.debug(f"Registered metric: {name}")

    def get_metric(self, name: str) -> Optional[Dict]:
        """Get a specific metric"""
        return self.metrics.get(name)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all registered metrics"""
        return self.metrics.copy()

    def clear_metrics(self) -> None:
        """Clear all metrics"""
        self.metrics.clear()
        self.logger.info("All metrics cleared")

    def get_summary(self) -> Dict[str, Any]:
        """Get registry summary"""
        return {
            "total_metrics": len(self.metrics),
            "created_at": self.created_at.isoformat(),
            "last_updated": max(
                [m["timestamp"] for m in self.metrics.values()]
            ) if self.metrics else None,
        }
