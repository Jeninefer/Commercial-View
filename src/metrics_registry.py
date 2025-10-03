import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict
import json

class MetricsRegistry:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_times: Dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        self.start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        if operation in self.start_times:
            latency = time.time() - self.start_times[operation]
            self.record_metric("latency_ms", latency * 1000.0, {"operation": operation})
            del self.start_times[operation]
            return latency
        return 0.0

    def record_metric(self, metric_name: str, value: Any, metadata: Optional[Dict] = None) -> None:
        self.metrics[metric_name].append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "value": value,
            "metadata": metadata or {}
        })

    def record_data_metrics(self, df: pd.DataFrame, operation: str = "processing") -> None:
        self.record_metric("n_rows", int(len(df)), {"operation": operation})
        denom = len(df) * len(df.columns) or 1
        completeness = 1 - (df.isnull().sum().sum() / denom)
        self.record_metric("quality_score", float(completeness), {"operation": operation})

    def record_rules_evaluated(self, n_rules: int, operation: str = "validation") -> None:
        self.record_metric("n_rules_evaluated", int(n_rules), {"operation": operation})

    def get_latest_metrics(self, hours_back: int = 24) -> Dict[str, Any]:
        cutoff = datetime.utcnow().timestamp() - (hours_back * 3600)
        out: Dict[str, Any] = {}
        for name, recs in self.metrics.items():
            recent = [r for r in recs if datetime.fromisoformat(r["timestamp"].replace("Z","")).timestamp() > cutoff]
            if recent:
                vals = [r["value"] for r in recent]
                out[name] = {
                    "count": len(vals),
                    "latest": vals[-1],
                    "avg": sum(vals)/len(vals) if vals else None,
                    "min": min(vals),
                    "max": max(vals)
                }
        return out

    def export_metrics(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            json.dump(dict(self.metrics), f, indent=2, default=str)

    def clear_old_metrics(self, hours_to_keep: int = 168) -> None:
        cutoff = datetime.utcnow().timestamp() - (hours_to_keep * 3600)
        for name in list(self.metrics.keys()):
            self.metrics[name] = [
                r for r in self.metrics[name]
                if datetime.fromisoformat(r["timestamp"].replace("Z","")).timestamp() > cutoff
            ]
