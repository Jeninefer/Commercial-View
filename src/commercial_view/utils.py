"""Utility modules for logging and metrics registry."""

import logging
from typing import Any

# Configure logger
logger = logging.getLogger("commercial_view")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class MetricsRegistry:
    """Registry for recording data metrics during operations."""
    
    def __init__(self):
        self.metrics = []
    
    def record_data_metrics(self, df: Any, operation: str) -> None:
        """Record metrics for a DataFrame operation.
        
        Args:
            df: DataFrame with metrics to record
            operation: Name of the operation
        """
        self.metrics.append({
            "operation": operation,
            "row_count": len(df) if hasattr(df, "__len__") else 0,
            "columns": list(df.columns) if hasattr(df, "columns") else []
        })
        logger.debug(f"Recorded metrics for {operation}: {len(df) if hasattr(df, '__len__') else 0} rows")


# Global registry instance
registry = MetricsRegistry()
