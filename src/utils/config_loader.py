"""
Configuration Loader for Commercial-View Analytics Pipeline

Loads and validates YAML configuration with environment variable support.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import re


class ConfigLoader:
    """Load and manage dashboard configuration"""

    def __init__(
        self, config_path: Optional[Path] = None, environment: str = "development"
    ):
        """
        Initialize configuration loader

        Args:
            config_path: Path to YAML config file
            environment: Environment name (development, staging, production)
        """
        self.environment = environment

        if config_path is None:
            # Default to config/dashboard_config.yaml
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "dashboard_config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._apply_environment_overrides()
        self._resolve_env_variables()
        self._set_dynamic_defaults()

    def _load_config(self) -> Dict:
        """Load YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)

        return config

    def _apply_environment_overrides(self):
        """Apply environment-specific overrides"""
        if (
            "environments" in self.config
            and self.environment in self.config["environments"]
        ):
            env_overrides = self.config["environments"][self.environment]
            self._deep_update(self.config, env_overrides)

    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Recursively update nested dictionaries"""
        for key, value in update_dict.items():
            if (
                key in base_dict
                and isinstance(base_dict[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _resolve_env_variables(self):
        """Resolve environment variable references (env:VAR_NAME)"""

        def resolve_value(value):
            if isinstance(value, str) and value.startswith("env:"):
                var_name = value[4:]
                env_value = os.getenv(var_name)
                if env_value is None:
                    print(f"⚠️  Environment variable {var_name} not set")
                return env_value
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(v) for v in value]
            return value

        self.config = resolve_value(self.config)

    def _set_dynamic_defaults(self):
        """Set dynamic default values"""
        # Set analysis_date to today if not specified
        if self.config["parameters"].get("analysis_date") is None:
            self.config["parameters"]["analysis_date"] = datetime.now().strftime(
                "%Y-%m-%d"
            )

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key_path: Dot-separated path (e.g., 'parameters.risk.npl_definitions')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_colors(self) -> Dict[str, str]:
        """Get color palette"""
        return self.get("outputs.colors", {})

    def get_targets(self) -> Dict:
        """Get 2026 targets"""
        return self.get("targets_2026", {})

    def get_risk_thresholds(self) -> Dict:
        """Get risk analysis thresholds"""
        return self.get("parameters.risk", {})

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(feature, False)

    def get_data_source_path(self, source_name: str) -> Optional[str]:
        """Get data source file path"""
        return self.get(f"data_sources.{source_name}")

    def validate(self) -> bool:
        """Validate configuration"""
        required_keys = ["data_sources", "parameters", "targets_2026", "outputs"]

        for key in required_keys:
            if key not in self.config:
                print(f"❌ Missing required config key: {key}")
                return False

        print("✅ Configuration validated successfully")
        return True

    def to_dict(self) -> Dict:
        """Export configuration as dictionary"""
        return self.config.copy()


def load_config(
    config_path: Optional[Path] = None, environment: str = None
) -> ConfigLoader:
    """
    Load configuration (convenience function)

    Args:
        config_path: Path to YAML config file
        environment: Environment name

    Returns:
        ConfigLoader instance
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")

    return ConfigLoader(config_path, environment)


# Example usage
if __name__ == "__main__":
    # Load config
    config = load_config()

    # Validate
    config.validate()

    # Test access
    print("\n📋 Configuration Test")
    print(f"Primary Color: {config.get('outputs.colors.primary')}")
    print(f"NPL 90 Threshold: {config.get('parameters.risk.npl_definitions.NPL90')}")
    print(
        f"2026 Portfolio Target: ${config.get('targets_2026.portfolio.total_portfolio_size'):,}"
    )
    print(f"Slack Export Enabled: {config.get('outputs.export.channels.slack')}")
