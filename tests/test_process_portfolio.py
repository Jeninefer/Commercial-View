"""Tests for the portfolio processing CLI entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_main_uses_default_pricing_path_when_config_empty(monkeypatch):
    """Ensure data loading functions are invoked with None when pricing config is empty."""

    # Import inside the test to ensure patches apply to the runtime module.
    from src import process_portfolio

    captured_args: Dict[str, Any] = {}

    def fake_load_config(_config_dir: str):
        # ``yaml.safe_load`` returns ``None`` for an empty file, which previously
        # triggered an AttributeError when accessing ``.get`` on ``None``.
        return {
            "pricing_config": None,
            "export_config": {},
        }

    def fake_load_loan_data(base_path=None):
        captured_args["loan_base_path"] = base_path
        return pd.DataFrame({"id": [1]})

    def fake_load_customer_data(base_path=None):
        captured_args["customer_base_path"] = base_path
        return pd.DataFrame({"id": [1]})

    monkeypatch.setattr(process_portfolio, "load_config", fake_load_config)
    monkeypatch.setattr(process_portfolio, "create_export_directories", lambda _cfg: None)
    monkeypatch.setattr(process_portfolio, "load_loan_data", fake_load_loan_data)
    monkeypatch.setattr(process_portfolio, "load_customer_data", fake_load_customer_data)

    monkeypatch.setattr(sys, "argv", ["process_portfolio.py", "--config", "dummy"], raising=False)

    process_portfolio.main()

    assert captured_args["loan_base_path"] is None
    assert captured_args["customer_base_path"] is None
