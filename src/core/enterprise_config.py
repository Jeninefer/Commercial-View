"""
Enterprise-grade configuration management for Commercial-View
Implements market-leading configuration practices with validation
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Environment types for configuration management"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class CommercialLendingLimits:
    """Commercial lending regulatory and business limits"""

    # Regulatory limits
    single_borrower_limit: float = 0.15  # 15% of capital
    industry_concentration_limit: float = 0.25  # 25% per industry
    geographic_concentration_limit: float = 0.30  # 30% per state

    # Risk limits
    maximum_ltv_ratio: float = 0.90  # 90% LTV
    minimum_dscr_ratio: float = 1.20  # 120% DSCR
    maximum_npl_tolerance: float = 0.05  # 5% NPL

    # Business limits
    minimum_loan_amount: float = 25000
    maximum_loan_amount: float = 25000000
    minimum_credit_score: int = 550
    maximum_days_past_due: int = 180


@dataclass
class KPITargets:
    """Key Performance Indicator targets for commercial lending"""

    # Portfolio targets
    target_portfolio_yield: float = 0.185  # 18.5%
    target_npl_rate: float = 0.025  # 2.5%
    target_collection_rate: float = 0.95  # 95%

    # Growth targets
    monthly_origination_target: float = 5000000  # $5M
    customer_acquisition_target: int = 50
    portfolio_growth_rate: float = 0.20  # 20% annually

    # Operational targets
    loan_processing_time_days: int = 5
    approval_rate_target: float = 0.65  # 65%
    customer_satisfaction_score: float = 4.5  # out of 5


class EnterpriseConfigManager:
    """
    Enterprise-grade configuration manager
    Handles environment-specific settings with validation
    """

    def __init__(self, environment: Optional[str] = None):
        self.environment = EnvironmentType(
            environment or os.getenv("ENVIRONMENT", "production")
        )
        self.config_directory = Path("configs")
        self.secrets_directory = Path("secrets")  # For encrypted secrets

        # Initialize configuration
        self._load_base_configuration()
        self._load_environment_specific_config()
        self._validate_configuration()

    def _load_base_configuration(self) -> None:
        """Load base configuration applicable to all environments"""
        self.base_config = {
            "application": {
                "name": "Commercial-View",
                "version": "1.0.0",
                "description": "Enterprise Commercial Lending Analytics Platform",
            },
            "commercial_lending": {
                "limits": CommercialLendingLimits(),
                "kpi_targets": KPITargets(),
            },
            "data_sources": {
                "google_drive_folder": "https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8",
                "refresh_interval_hours": 6,
                "data_retention_days": 2555,  # 7 years for regulatory compliance
            },
            "integrations": {
                "openai": {"model": "gpt-4-turbo", "max_tokens": 4000},
                "anthropic": {"model": "claude-3-sonnet", "max_tokens": 4000},
                "google_gemini": {"model": "gemini-pro", "max_tokens": 4000},
                "hubspot": {"api_version": "v3"},
                "slack": {"channel": "#commercial-lending-alerts"},
            },
        }

    def _load_environment_specific_config(self) -> None:
        """Load environment-specific configurations"""
        env_config_file = self.config_directory / f"{self.environment.value}.yml"

        if env_config_file.exists():
            with open(env_config_file, "r") as f:
                env_config = yaml.safe_load(f)
                self._merge_configurations(env_config)

        # Load sensitive environment variables
        self._load_environment_variables()

    def _merge_configurations(self, env_config: Dict[str, Any]) -> None:
        """Recursively merge environment-specific configuration"""

        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        self.base_config = deep_merge(self.base_config, env_config)

    def _load_environment_variables(self) -> None:
        """Load sensitive configuration from environment variables"""
        self.sensitive_config = {
            "api_keys": {
                "openai": os.getenv("OPENAI_API_KEY"),
                "anthropic": os.getenv("ANTHROPIC_API_KEY"),
                "google": os.getenv("GOOGLE_API_KEY"),
                "hubspot": os.getenv("HUBSPOT_API_KEY"),
            },
            "database": {
                "url": os.getenv("DATABASE_URL"),
                "username": os.getenv("DB_USERNAME"),
                "password": os.getenv("DB_PASSWORD"),
            },
            "integrations": {
                "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),
                "google_credentials": os.getenv("GOOGLE_CREDENTIALS_PATH"),
                "sendgrid_key": os.getenv("SENDGRID_API_KEY"),
            },
        }

    def _validate_configuration(self) -> None:
        """Validate configuration completeness and correctness"""
        validation_errors = []

        # Validate commercial lending limits
        limits = self.get_commercial_limits()
        if limits.minimum_loan_amount >= limits.maximum_loan_amount:
            validation_errors.append("Minimum loan amount must be less than maximum")

        # Validate KPI targets
        targets = self.get_kpi_targets()
        if targets.target_npl_rate >= 1.0:
            validation_errors.append("NPL rate target must be less than 100%")

        # Validate environment variables for production
        if self.environment == EnvironmentType.PRODUCTION:
            required_vars = [
                "OPENAI_API_KEY",
                "GOOGLE_CREDENTIALS_PATH",
                "DATABASE_URL",
            ]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                validation_errors.append(
                    f"Missing required environment variables: {missing_vars}"
                )

        if validation_errors:
            raise ValueError(f"Configuration validation failed: {validation_errors}")

        logger.info(
            f"✅ Configuration validated for {self.environment.value} environment"
        )

    def get_commercial_limits(self) -> CommercialLendingLimits:
        """Get the commercial lending limits configuration"""
        return self.base_config["commercial_lending"]["limits"]

    def get_kpi_targets(self) -> KPITargets:
        """Get the KPI targets configuration"""
        return self.base_config["commercial_lending"]["kpi_targets"]

    def get_data_sources_config(self) -> Dict[str, Any]:
        """Get the data sources configuration"""
        return self.base_config["data_sources"]

    def get_integrations_config(self) -> Dict[str, Any]:
        """Get the integrations configuration"""
        return self.base_config["integrations"]

    def get_sensitive_config(self) -> Dict[str, Any]:
        """Get the sensitive configuration (e.g., API keys, database credentials)"""
        return self.sensitive_config

    def to_json(self) -> str:
        """Convert the entire configuration to JSON format"""
        return json.dumps(self.base_config, default=lambda o: o.__dict__, indent=2)

    def to_yaml(self) -> str:
        """Convert the entire configuration to YAML format"""
        return yaml.dump(self.base_config, default_flow_style=False)

    def save_to_file(self, file_path: Path, file_format: str = "yaml") -> None:
        """Save the configuration to a file in the specified format (YAML or JSON)"""
        file_path.parent.mkdir(
            parents=True, exist_ok=True
        )  # Create parent directories if they don't exist

        if file_format == "yaml":
            with open(file_path, "w") as f:
                yaml.dump(self.base_config, f, default_flow_style=False)
        elif file_format == "json":
            with open(file_path, "w") as f:
                json.dump(self.base_config, f, default=lambda o: o.__dict__, indent=2)
        else:
            raise ValueError("Unsupported file format. Use 'yaml' or 'json'.")

        logger.info(f"Configuration saved to {file_path} as {file_format.upper()}")
