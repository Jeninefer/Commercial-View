from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pytest

from data_loader import DataLoader


@pytest.fixture()
def sample_abaco_dataset(tmp_path: Path) -> Path:
    base_dir = tmp_path / "pricing"
    base_dir.mkdir()

    loan_data = pd.DataFrame(
        {
            "Company": ["Acme Corp"],
            "Customer ID": [1001],
            "Cliente": ["Cliente Uno"],
            "Pagador": ["Pagador Uno"],
            "Loan ID": ["LN-001"],
            "Application ID": ["APP-001"],
            "Product Type": ["Working Capital"],
            "Loan Currency": ["PEN"],
            "Disbursement Amount": [10000],
            "Outstanding Loan Value": [8000],
            "Interest Rate APR": [12.5],
            "Disbursement Date": ["2023-01-15"],
            "Term": [180],
            "Term Unit": ["Days"],
            "Payment Frequency": ["Monthly"],
            "Days in Default": [0],
            "Loan Status": ["Current"],
            "past_due_amount": [0],
            "first_arrears_date": ["2023-02-01"],
            "last_payment_date": ["2023-02-01"],
            "last_due_date": ["2023-02-28"],
            "reference_date": ["2023-03-01"],
        }
    )

    payment_schedule = pd.DataFrame(
        {
            "Loan ID": ["LN-001"],
            "Payment Date": ["2023-02-28"],
            "Total Payment": [850],
            "Principal Payment": [700],
            "Interest Payment": [120],
            "Fee Payment": [20],
            "Tax Payment": [10],
            "Outstanding Loan Value": [7800],
            "Currency": ["PEN"],
            "TPV": ["POS"],
        }
    )

    historic_real_payment = payment_schedule.assign(
        **{
            "True Payment Date": ["2023-02-27"],
            "True Payment Status": ["On Time"],
        }
    )

    customer_data = pd.DataFrame(
        {
            "Business Year Founded": [2001],
            "Equifax Score": [720],
            "Category": ["SMB"],
            "Credit Line Category": ["Gold"],
            "Subcategory": ["Manufacturing"],
            "Credit Line Subcategory": ["Equipment"],
            "Industry": ["Manufacturing"],
            "Birth Year": [1980],
            "Occupation": ["Engineer"],
            "Client Type": ["Corporate"],
            "Location City": ["Lima"],
            "Location State/Province": ["Lima"],
            "Location Country": ["Peru"],
            "Customer ID": [1001],
            "Customer Name": ["Cliente Uno"],
            "KAM": ["Ana Perez"],
            "Credit Line": [50000],
        }
    )

    collateral = pd.DataFrame(
        {
            "Customer ID": [1001],
            "Customer Name": ["Cliente Uno"],
            "Loan ID": ["LN-001"],
            "Collateral ID": ["COL-001"],
            "Collateral Original": [15000],
            "Collateral Current": [14000],
        }
    )

    dataset_files = {
        "Abaco - Loan Tape_Loan Data_Table.csv": loan_data,
        "Abaco - Loan Tape_Payment Schedule_Table.csv": payment_schedule,
        "Abaco - Loan Tape_Historic Real Payment_Table.csv": historic_real_payment,
        "Abaco - Loan Tape_Customer Data_Table.csv": customer_data,
        "Abaco - Loan Tape_Collateral_Table.csv": collateral,
    }

    for filename, dataframe in dataset_files.items():
        dataframe.to_csv(base_dir / filename, index=False)

    return base_dir


def test_load_all_datasets_populates_expected_keys(
    sample_abaco_dataset: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(sample_abaco_dataset))

    loader = DataLoader()
    datasets = loader.load_all_datasets()

    expected_keys = {
        "loan_data",
        "payment_schedule",
        "historic_real_payment",
        "customer_data",
        "collateral",
    }

    assert expected_keys.issubset(datasets.keys())
    assert all(not datasets[name].empty for name in expected_keys)
