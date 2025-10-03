"""KPI Exporter module for exporting KPI data to JSON files."""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


class KPIExporter:
    """Exports KPI data to JSON files with timestamps."""

    def __init__(self, export_path: str = "exports"):
        """Initialize the KPI Exporter.
        
        Args:
            export_path: Directory path where JSON files will be exported.
        """
        self.export_path = export_path

    def _export_json(self, payload: Dict[str, Any], name: str) -> str:
        """Export KPI data to a JSON file with timestamp.
        
        Args:
            payload: Dictionary containing KPI data to export.
            name: Base name for the exported file.
            
        Returns:
            The full path to the exported JSON file.
        """
        os.makedirs(self.export_path, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        fp = os.path.join(self.export_path, f"{name}_{ts}.json")
        with open(fp, "w") as f:
            json.dump(payload, f, indent=2, default=str)
        logger.info(f"KPIs exported: {fp}")
        return fp
