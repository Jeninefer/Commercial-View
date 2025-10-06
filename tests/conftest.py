"""Shared pytest fixtures and runtime guards for the Commercial-View test suite."""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import pytest


project_root = Path(__file__).parent.parent


def _warn_if_outside_virtualenv() -> None:
    """Emit a helpful warning when tests are executed outside a virtualenv."""
    in_virtualenv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if not in_virtualenv:
        warnings.warn(
            "Tests are running outside a Python virtual environment. "
            "For reproducible results prefer activating the project venv.",
            RuntimeWarning,
            stacklevel=2,
        )


# Add the project root to the path so imports work properly for all tests
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session", autouse=True)
def configure_env() -> None:
    """Configure deterministic environment defaults for the test suite."""
    _warn_if_outside_virtualenv()

    os.environ.setdefault(
        "COMMERCIAL_VIEW_DATA_PATH", str(project_root / "tests" / "data")
    )

    # Ensure the shared test data directory exists for fixtures that rely on it
    test_data_dir = project_root / "tests" / "data"
    test_data_dir.mkdir(exist_ok=True)

    yield
