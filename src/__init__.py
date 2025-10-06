"""Commercial-View package bootstrap utilities."""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = "1.0.0"
__title__ = "Commercial-View"
__description__ = "Enterprise commercial lending analytics and portfolio management platform"
__author__ = "Commercial-View Team"
__license__ = "Proprietary"

PACKAGE_INFO: Dict[str, Any] = {
    "version": __version__,
    "title": __title__,
    "description": __description__,
    "author": __author__,
    "license": __license__,
    "python_requires": ">=3.10",
    "project_root": str(Path(__file__).resolve().parent),
}

_MODULE_GROUPS: Dict[str, tuple[str, ...]] = {
    "core_modules": (
        "src.data_loader",
        "src.pipeline",
    ),
    "analytics_modules": (
        "src.feature_engineer",
        "src.metrics_calculator",
        "src.portfolio_optimizer",
    ),
    "utility_modules": (
        "src.process_portfolio",
        "src.google_drive_exporter",
    ),
}


def _module_available(module_path: str) -> bool:
    """Return True when *module_path* can be imported without executing it."""
    return importlib.util.find_spec(module_path) is not None


def _collect_import_errors() -> Dict[str, list[str]]:
    """List the modules that are not available per module group."""
    missing: Dict[str, list[str]] = {}
    for group, modules in _MODULE_GROUPS.items():
        unavailable = [m for m in modules if not _module_available(m)]
        if unavailable:
            missing[group] = unavailable
    return missing


def _group_status(group: str) -> bool:
    return all(_module_available(module) for module in _MODULE_GROUPS[group])


def get_package_info() -> Dict[str, Any]:
    """Return metadata and module availability for the Commercial-View package."""
    return {
        **PACKAGE_INFO,
        "modules_status": {group: _group_status(group) for group in _MODULE_GROUPS},
        "import_errors": _collect_import_errors(),
        "production_ready": _group_status("core_modules"),
    }


def get_available_features() -> Dict[str, bool]:
    """Summarise high-level feature availability."""
    core_available = _group_status("core_modules")
    analytics_available = _group_status("analytics_modules")
    utility_available = _group_status("utility_modules")

    return {
        "portfolio_analytics": core_available,
        "dpd_analysis": analytics_available,
        "portfolio_optimization": analytics_available,
        "export_tools": utility_available,
    }


def validate_environment() -> Dict[str, Any]:
    """Provide a quick diagnostic of the runtime environment."""
    python_ok = sys.version_info >= (3, 10)
    diagnostics = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_compatible": python_ok,
        "package_path": str(Path(__file__).parent),
        "features": get_available_features(),
        "issues": [],
        "recommendations": [],
    }

    if not python_ok:
        diagnostics["issues"].append("Python 3.10 or newer is required")
        diagnostics["recommendations"].append("Upgrade to Python 3.11 for best results")

    missing_groups = _collect_import_errors()
    if missing_groups:
        diagnostics["issues"].append("Some optional modules are unavailable")
        diagnostics["recommendations"].extend(
            [f"Install dependencies for: {', '.join(modules)}" for modules in missing_groups.values()]
        )

    return diagnostics


def get_integration_status() -> Dict[str, Dict[str, Any]]:
    """Report the configuration status for supported integrations."""
    integrations = {
        "google_drive": {
            "available": _module_available("src.google_drive_exporter"),
            "configured": bool(os.getenv("GOOGLE_CREDENTIALS_PATH")),
        },
        "slack": {
            "available": True,
            "configured": bool(os.getenv("SLACK_WEBHOOK_URL")),
        },
    }

    for name, info in integrations.items():
        info["ready"] = info["available"] and info["configured"]
    return integrations


def create_enterprise_analyzer() -> Optional[Dict[str, Any]]:
    """Instantiate core analytics helpers when the dependencies are available."""
    if not _group_status("analytics_modules"):
        logger.warning("Analytics modules are not fully available; cannot build analyzer.")
        return None

    try:
        from .feature_engineer import FeatureEngineer
        from .metrics_calculator import MetricsCalculator
        from .portfolio_optimizer import PortfolioOptimizer
    except Exception as exc:  # pragma: no cover - defensive safety net
        logger.error("Unable to create enterprise analyzer: %s", exc)
        return None

    return {
        "feature_engineer": FeatureEngineer(),
        "metrics_calculator": MetricsCalculator(),
        "portfolio_optimizer": PortfolioOptimizer(),
    }


__all__ = [
    "PACKAGE_INFO",
    "get_package_info",
    "get_available_features",
    "validate_environment",
    "get_integration_status",
    "create_enterprise_analyzer",
    "__version__",
    "__title__",
]
