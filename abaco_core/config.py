"""
Configuration management for Commercial-View.

Loads and provides access to the abaco_manifest.json schema and constraints.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_MANIFEST_PATH = Path("./abaco_manifest.json")


class Config:
    """
    Configuration loader and accessor for portfolio manifest.
    
    Loads the abaco_manifest.json file containing bucket definitions,
    optimizer constraints, and alert thresholds.
    
    Example:
        >>> config = Config()
        >>> apr_buckets = config.get("apr_buckets")
        >>> optimizer = config.optimizer
    """
    
    def __init__(self, manifest_path: Path | str = DEFAULT_MANIFEST_PATH):
        """
        Initialize configuration from manifest file.
        
        Args:
            manifest_path: Path to the manifest JSON file.
                          Defaults to ./abaco_manifest.json
        
        Raises:
            FileNotFoundError: If manifest file doesn't exist.
            json.JSONDecodeError: If manifest is invalid JSON.
        """
        self.path = Path(manifest_path)
        self.data: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """
        Reload configuration from manifest file.
        
        Raises:
            FileNotFoundError: If manifest file doesn't exist.
            json.JSONDecodeError: If manifest is invalid JSON.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.path}")
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key to retrieve.
            default: Default value if key not found.
        
        Returns:
            Configuration value or default.
        """
        return self.data.get(key, default)

    @property
    def optimizer(self) -> Dict[str, Any]:
        """
        Get optimizer constraints configuration.
        
        Returns:
            Dictionary containing target_mix, hard_limits, and priority_weights.
        """
        return self.data.get("optimizer_constraints", {})

    @property
    def alerts(self) -> Dict[str, Any]:
        """
        Get alert thresholds configuration.
        
        Returns:
            Dictionary containing alert rules for concentration, risk, yield,
            liquidity, and growth.
        """
        return self.data.get("alerts", {})
