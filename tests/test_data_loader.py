from pathlib import Path
import sys

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import DataLoader, PRICING_FILENAMES


@pytest.fixture()
def sample_pricing_dir(tmp_path: Path) -> Path:
    base_dir = tmp_path / "pricing"
    base_dir.mkdir()

    sample_df = pd.DataFrame(
        {
            "id": [1, 2],
            "value": [100, 200],
        }
    )

    for filename in PRICING_FILENAMES.values():
        sample_df.to_csv(base_dir / filename, index=False)

    return base_dir


def test_loaders_respect_environment_override(sample_pricing_dir: Path, monkeypatch) -> None:
    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(sample_pricing_dir))
    loader = DataLoader()

    assert not loader.load_loan_data().empty
    assert not loader.load_historic_real_payment().empty
    assert not loader.load_payment_schedule().empty
    assert not loader.load_customer_data().empty
    assert not loader.load_collateral().empty


def test_loaders_use_overridden_base_path(sample_pricing_dir: Path) -> None:
    loader = DataLoader(base_path=sample_pricing_dir)
    loan_df = loader.load_loan_data()
    customer_df = loader.load_customer_data()

    assert loan_df.equals(customer_df)
    assert loan_df.iloc[0]["id"] == 1


def test_missing_file_raises_clear_error(sample_pricing_dir: Path) -> None:
    missing_file = PRICING_FILENAMES["customer_data"]
    (sample_pricing_dir / missing_file).unlink()
    loader = DataLoader(base_path=sample_pricing_dir)

    with pytest.raises(FileNotFoundError) as exc:
        loader.load_customer_data()

    assert "CSV file not found" in str(exc.value)
    assert missing_file in str(exc.value)