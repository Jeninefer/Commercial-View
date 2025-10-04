from pathlib import Path
import sys

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import data_loader


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

    for filename in data_loader.PRICING_FILENAMES.values():
        sample_df.to_csv(base_dir / filename, index=False)

    return base_dir


def test_loaders_use_overridden_base_path(sample_pricing_dir: Path) -> None:
    loan_df = data_loader.load_loan_data(sample_pricing_dir)
    customer_df = data_loader.load_customer_data(sample_pricing_dir)

    assert loan_df.equals(customer_df)
    assert loan_df.iloc[0]["id"] == 1


def test_missing_file_raises_clear_error(sample_pricing_dir: Path) -> None:
    missing_file = data_loader.PRICING_FILENAMES["customer_data"]
    (sample_pricing_dir / missing_file).unlink()

    with pytest.raises(FileNotFoundError) as exc:
        data_loader.load_customer_data(sample_pricing_dir)

    assert missing_file in str(exc.value)
