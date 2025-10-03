"""
Configuration module for abaco_core.

Provides Config class for loading and managing optimizer configuration
from abaco_manifest.json or default values.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("abaco_core.config")


class Config:
    """
    Configuration loader for ABACO optimizer.
    
    Reads configuration from abaco_manifest.json if available,
    otherwise uses default values.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Config.
        
        Args:
            config_path: Path to abaco_manifest.json. If None, searches
                        for it in standard locations or uses defaults.
        """
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or return defaults.
        
        Returns:
            Dictionary containing configuration values.
        """
        if self.config_path:
            path = Path(self.config_path)
        else:
            # Try standard locations
            candidates = [
                Path("abaco_manifest.json"),
                Path("config/abaco_manifest.json"),
                Path("../abaco_manifest.json"),
            ]
            path = next((p for p in candidates if p.exists()), None)
        
        if path and path.exists():
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Loaded configuration from {path}")
                    return config
            except Exception as e:
                logger.warning(f"Failed to load config from {path}: {e}")
        
        # Return default configuration
        logger.info("Using default configuration")
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """
        Return default configuration.
        
        Returns:
            Dictionary with default optimizer configuration.
        """
        return {
            "optimizer_constraints": {
                "target_mix": {
                    "apr": {},
                    "line": {},
                    "industry": {},
                    "payer": {}
                },
                "hard_limits": {
                    "max_concentration_per_customer": 0.10,
                    "max_concentration_per_industry": 0.15
                },
                "priority_weights": {
                    "apr": 0.6,
                    "term_fit": 0.35,
                    "origination_count": 0.05
                }
            }
        }
    
    @property
    def optimizer(self) -> Dict[str, Any]:
        """
        Get optimizer configuration section.
        
        Returns:
            Dictionary containing optimizer_constraints configuration.
        """
        return self._config.get("optimizer_constraints", {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation for nested keys).
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
