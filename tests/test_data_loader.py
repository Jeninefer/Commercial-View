from pathlib import Path
import sys
from typing import Dict, Tuple

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import data_loader


@pytest.fixture()
def sample_pricing_dir(tmp_path: Path) -> Tuple[Path, Dict[str, pd.DataFrame]]:
    base_dir = tmp_path / "pricing"
    base_dir.mkdir()

    sample_frames: Dict[str, pd.DataFrame] = {}
    for index, (key, filename) in enumerate(data_loader.PRICING_FILENAMES.items(), start=1):
        df = pd.DataFrame(
            {
                "dataset": [key],
                "value": [index],
            }
        )
        df.to_csv(base_dir / filename, index=False)
        sample_frames[key] = df

    return base_dir, sample_frames


def test_loaders_use_overridden_base_path(
    sample_pricing_dir: Tuple[Path, Dict[str, pd.DataFrame]]
) -> None:
    base_dir, expected_frames = sample_pricing_dir

    # Explicit mapping of keys to loader functions
    loaders = {
        "customer_data": data_loader.load_customer_data,
        "product_data": data_loader.load_product_data,
        "pricing_data": data_loader.load_pricing_data,
    }

    # Ensure all keys in PRICING_FILENAMES have a loader
    assert set(loaders.keys()) == set(data_loader.PRICING_FILENAMES.keys())
    for key, loader in loaders.items():
        loaded = loader(base_dir)
        assert_frame_equal(loaded, expected_frames[key])


def test_missing_file_raises_clear_error(
    sample_pricing_dir: Tuple[Path, Dict[str, pd.DataFrame]]
) -> None:
    base_dir, _ = sample_pricing_dir
    missing_file = data_loader.PRICING_FILENAMES["customer_data"]
    (base_dir / missing_file).unlink()

    with pytest.raises(FileNotFoundError) as exc:
        data_loader.load_customer_data(base_dir)

    assert missing_file in str(exc.value)
