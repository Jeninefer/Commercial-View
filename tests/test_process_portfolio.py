from __future__ import annotations

import os
from pathlib import Path
import sys

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import data_loader
from src import process_portfolio


def _write_sample_pricing_data(base_dir: Path) -> pd.DataFrame:
    base_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        {
            "id": [101, 202],
            "value": [1234, 5678],
        }
    )

    for filename in data_loader.PRICING_FILENAMES.values():
        df.to_csv(base_dir / filename, index=False)

    return df


def test_config_pricing_path_used_when_no_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(process_portfolio.PRICING_DATA_ENV_VAR, raising=False)

    alt_pricing_dir = tmp_path / "alt_pricing"
    expected_df = _write_sample_pricing_data(alt_pricing_dir)

    config_dir = tmp_path / "config"
    config_dir.mkdir()

    relative_path = os.path.relpath(alt_pricing_dir, start=PROJECT_ROOT)
    (config_dir / "pricing_config.yml").write_text(
        f"pricing_data_path: {relative_path}\n",
        encoding="utf-8",
    )

    configs = process_portfolio.load_config(str(config_dir))
    pricing_config = configs.get("pricing_config") or {}

    resolved_dir = process_portfolio.resolve_pricing_data_dir(
        cli_override=None,
        env_override=None,
        config_override=pricing_config.get("pricing_data_path"),
    )

    assert resolved_dir == alt_pricing_dir.resolve()

    loaded_df = data_loader.load_loan_data(resolved_dir)

    pd.testing.assert_frame_equal(loaded_df, expected_df)
