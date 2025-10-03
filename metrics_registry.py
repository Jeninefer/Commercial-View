import time
import json
import logging
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class MetricsRegistry:
    """Registry for collecting and managing performance metrics."""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times: Dict[str, float] = {}

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def start_timer(self, operation: str) -> None:
        self.start_times[operation] = time.perf_counter()

    def end_timer(self, operation: str) -> float:
        start = self.start_times.pop(operation, None)
        if start is None:
            return 0.0
        latency = time.perf_counter() - start
        self.record_metric('latency_ms', round(latency * 1000, 3), {'operation': operation})
        return latency

    def record_metric(self, metric_name: str, value: Any, metadata: Optional[Dict] = None) -> None:
        self.metrics[metric_name].append({
            'timestamp': self._now_iso(),
            'value': value,
            'metadata': metadata or {}
        })

    def record_data_metrics(self, df: pd.DataFrame, operation: str = 'processing') -> None:
        n_rows = int(len(df)) if isinstance(df, pd.DataFrame) else 0
        self.record_metric('n_rows', n_rows, {'operation': operation})
        if n_rows > 0:
            denom = max(n_rows * len(df.columns), 1)
            nulls = int(df.isnull().sum().sum())
            completeness = float(1 - (nulls / denom))
        else:
            completeness = 0.0
        self.record_metric('quality_score', round(completeness, 6), {'operation': operation})

    def record_rules_evaluated(self, n_rules: int, operation: str = 'validation') -> None:
        self.record_metric('n_rules_evaluated', int(n_rules), {'operation': operation})

    def get_latest_metrics(self, hours_back: int = 24) -> Dict[str, Any]:
        cutoff = datetime.now(timezone.utc).timestamp() - (hours_back * 3600)
        out: Dict[str, Any] = {}
        for name, recs in self.metrics.items():
            recent = [r for r in recs if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff]
            if not recent:
                continue
            vals = [r['value'] for r in recent]
            try:
                numeric = [float(v) for v in vals]
                out[name] = {
                    'count': len(numeric),
                    'latest': numeric[-1],
                    'avg': sum(numeric) / len(numeric),
                    'min': min(numeric),
                    'max': max(numeric),
                }
            except Exception:
                out[name] = {'count': len(vals), 'latest': vals[-1]}
        return out

    def export_metrics(self, filepath: str) -> None:
        with open(filepath, 'w') as f:
            json.dump(dict(self.metrics), f, indent=2, default=str)

    def clear_old_metrics(self, hours_to_keep: int = 168) -> None:
        cutoff = datetime.now(timezone.utc).timestamp() - (hours_to_keep * 3600)
        for name in list(self.metrics.keys()):
            self.metrics[name] = [
                r for r in self.metrics[name]
                if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff
            ]


logger.info("Module 3: Feature Engineering loaded successfully")
