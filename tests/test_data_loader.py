import sys
from pathlib import Path

import pytest

from src import data_loader


@pytest.fixture
def sample_pricing_dir(tmp_path):
    pricing_dir = tmp_path / "pricing"
    pricing_dir.mkdir()

    sample_data = "id,amount\n1,100\n"
    files = {
        "Abaco - Loan Tape_Loan Data_Table.csv": sample_data,
        "Abaco - Loan Tape_Historic Real Payment_Table.csv": sample_data,
        "Abaco - Loan Tape_Payment Schedule_Table.csv": sample_data,
        "Abaco - Loan Tape_Customer Data_Table.csv": sample_data,
        "Abaco - Loan Tape_Collateral_Table.csv": sample_data,
    }

    for filename, content in files.items():
        (pricing_dir / filename).write_text(content)

    return pricing_dir


def test_loaders_respect_environment_override(sample_pricing_dir, monkeypatch):
    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(sample_pricing_dir))

    assert not data_loader.load_loan_data().empty
    assert not data_loader.load_historic_real_payment().empty
    assert not data_loader.load_payment_schedule().empty
    assert not data_loader.load_customer_data().empty
    assert not data_loader.load_collateral().empty


def test_missing_file_raises_clear_error(sample_pricing_dir, monkeypatch):
    missing_file = sample_pricing_dir / "Abaco - Loan Tape_Loan Data_Table.csv"
    missing_file.unlink()
    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(sample_pricing_dir))

    with pytest.raises(FileNotFoundError) as error:
        data_loader.load_loan_data()

    expected_message = "CSV file not found"
    assert expected_message in str(error.value)
