
import json
from pathlib import Path
import sys

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import DataLoader


@pytest.fixture()
def sample_data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture()
def sample_manifest(tmp_path: Path, sample_data_dir: Path) -> Path:
    manifest_path = tmp_path / "manifest.json"
    manifest_data = {
        "sources": {
            "files": [
                {
                    "name": "loan_data",
                    "glob": "data/loan_data.csv",
                },
                {
                    "name": "customer_data",
                    "glob": "data/customer_data.csv",
                },
            ]
        }
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f)

    # Create dummy data files
    sample_df_loan = pd.DataFrame({"loan_id": [1, 2], "loan_value": [100, 200]})
    sample_df_loan.to_csv(sample_data_dir / "loan_data.csv", index=False)

    sample_df_customer = pd.DataFrame({"customer_id": [1, 2], "customer_name": ["A", "B"]})
    sample_df_customer.to_csv(sample_data_dir / "customer_data.csv", index=False)

    return manifest_path


def test_load_all_datasets(sample_manifest: Path) -> None:
    loader = DataLoader(manifest_path=str(sample_manifest))
    datasets = loader.load_all_datasets()

    assert "loan_data" in datasets
    assert "customer_data" in datasets
    assert len(datasets) == 2

    loan_df = datasets["loan_data"]
    assert "loan_id" in loan_df.columns
    assert len(loan_df) == 2

    customer_df = datasets["customer_data"]
    assert "customer_id" in customer_df.columns
    assert len(customer_df) == 2


def test_missing_manifest_raises_error() -> None:
    with pytest.raises(FileNotFoundError):
        DataLoader(manifest_path="non_existent_manifest.json")


def test_empty_manifest_loads_no_datasets(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump({}, f)

    loader = DataLoader(manifest_path=str(manifest_path))
    datasets = loader.load_all_datasets()
    assert len(datasets) == 0
