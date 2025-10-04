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

    for index, filename in enumerate(data_loader.PRICING_FILENAMES.values(), start=1):
        sample_df = pd.DataFrame(
            {
                "id": [index, index + 1],
                "value": [index * 100, (index + 1) * 100],
            }
        )
        sample_df.to_csv(base_dir / filename, index=False)

    return base_dir


def test_loaders_use_overridden_base_path(sample_pricing_dir: Path) -> None:
    loan_df = data_loader.load_loan_data(sample_pricing_dir)
    customer_df = data_loader.load_customer_data(sample_pricing_dir)

    assert loan_df.iloc[0]["id"] == 1
    assert loan_df.iloc[-1]["value"] == 200
    assert customer_df.iloc[0]["id"] == 4
    assert customer_df.iloc[-1]["value"] == 500


def test_missing_file_raises_clear_error(sample_pricing_dir: Path) -> None:
    missing_file = data_loader.PRICING_FILENAMES["customer_data"]
    (sample_pricing_dir / missing_file).unlink()

    with pytest.raises(FileNotFoundError) as exc:
        data_loader.load_customer_data(sample_pricing_dir)

    assert missing_file in str(exc.value)


@pytest.mark.parametrize(
    "loader_func",
    [
        data_loader.load_loan_data,
        data_loader.load_historic_real_payment,
        data_loader.load_payment_schedule,
        data_loader.load_customer_data,
        data_loader.load_collateral,
    ],
)
def test_all_loader_functions_read_expected_files(
    loader_func, sample_pricing_dir: Path
) -> None:
    loaded_df = loader_func(sample_pricing_dir)

    assert isinstance(loaded_df, pd.DataFrame)
    assert not loaded_df.empty
