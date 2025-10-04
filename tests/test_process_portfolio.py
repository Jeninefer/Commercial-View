"""Tests for the process_portfolio entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import process_portfolio


def test_main_uses_default_pricing_directory_for_empty_config(monkeypatch, tmp_path):
    """An empty pricing config should not override the default data directory."""

    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Simulate an empty pricing_config.yml file.
    (config_dir / "pricing_config.yml").write_text("")

    # Stub the CLI arguments consumed by ``main``.
    parsed_args = argparse.Namespace(config=str(config_dir), data=None)

    def _fake_parse_args(self):  # pragma: no cover - exercised via main
        return parsed_args

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", _fake_parse_args)

    loan_call = {}

    def _fake_load_loan_data(base_path=None):
        loan_call["value"] = base_path
        return pd.DataFrame({"loan_id": []})

    def _fake_load_customer_data(base_path=None):
        return pd.DataFrame({"customer_id": []})

    monkeypatch.setattr(process_portfolio, "load_loan_data", _fake_load_loan_data)
    monkeypatch.setattr(process_portfolio, "load_customer_data", _fake_load_customer_data)
    monkeypatch.setattr(process_portfolio, "create_export_directories", lambda _: None)

    # ``main`` should complete without raising and fall back to the default path
    # (represented by ``None`` in the loader call) when the pricing config is empty.
    process_portfolio.main()

    assert loan_call["value"] is None
