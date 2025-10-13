"""
Commercial-View Data Loader - Abaco Integration
Loads and validates 48,853 Abaco records based on validated schema structure
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)


class DataLoaderError(Exception):
    """Exception raised for data loading errors."""
    pass


# Expected record counts for Abaco integration
# 48,853 = 16,205 (dataset A) + 16,443 (dataset B) + 16,205 (dataset C)
ABACO_RECORDS_EXPECTED = 48853


def validate_abaco_schema(schema: Dict[str, Any]) -> bool:
    """
    Validate the structure of an Abaco schema.

    Args:
        schema (Dict[str, Any]): The Abaco schema dictionary. Expected to contain a "datasets" key,
            whose value is a dictionary mapping dataset names to dictionaries with at least the keys:
            - "rows" (int): Number of records in the dataset.
            - "exists" (bool): Whether the dataset is present and should be counted.

    Returns:
        bool: True if the sum of "rows" for all datasets with "exists" set to True equals 48,853 (the expected
            total number of Abaco records); False otherwise or if the schema is malformed.

    A valid Abaco schema structure must have:
        - A "datasets" key at the top level.
        - Each dataset under "datasets" must be a dictionary with "rows" (int) and "exists" (bool) keys.
        - The sum of "rows" for all datasets where "exists" is True must be exactly 48,853.
    """
    try:
        datasets = schema.get("datasets", {})
        total_records = sum(
            dataset.get("rows", 0)
            for dataset in datasets.values()
            if dataset.get("exists", False)
        )
        return total_records == ABACO_RECORDS_EXPECTED
    except (KeyError, TypeError, AttributeError) as e:
        logger.error(f"Schema validation error: {e}", exc_info=True)
        return False


class DataLoader:
    """
    Data loader for Abaco loan tape processing.
    Handles exact schema structure: 16,205 + 16,443 + 16,205 = 48,853 records
    """

    def __init__(self, data_dir: str = "data", data_path: str = None, config_dir: str = "config"):
        """
        Initialize DataLoader with Abaco-specific configuration.

        Args:
            data_dir (str): Path to the directory containing data files. This is the preferred parameter.
            data_path (str, optional): [DEPRECATED] Path to the data directory. If both `data_dir` and `data_path` are provided,
                `data_path` takes precedence. This parameter is maintained for backward compatibility and will be removed in a future release.
            config_dir (str): Path to the configuration directory.

        Note:
            Use `data_dir` to specify the data directory. `data_path` is deprecated and should not be used in new code.
        """
        # Support both data_dir and data_path for backwards compatibility
        if data_dir is not None and data_path is not None:
            # Both provided: data_path takes precedence
            self.data_dir = Path(data_path)
        elif data_path is not None:
            self.data_dir = Path(data_path)
        else:
            self.data_dir = Path(data_dir)
        
        self.config_dir = Path(config_dir)

        # Try both locations for schema
        self.schema_paths = [
            self.config_dir / "abaco_schema_autodetected.json",
            Path("/Users/jenineferderas/Downloads/abaco_schema_autodetected.json"),
        ]

        self.expected_records = {
            "loan_data": 16205,
            "payment_history": 16443,
            "payment_schedule": 16205,
            "total": 48853,
        }

    def load_abaco_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load complete Abaco dataset based on validated schema structure.

        Returns:
            Dict containing DataFrames for loan_data, payment_history, payment_schedule
        """
        print("🏦 Loading Abaco loan tape data...")
        print(f"📊 Expected: {self.expected_records['total']:,} total records")

        # Validate schema first
        schema_valid = self.validate_schema()
        if not schema_valid:
            print("⚠️  Schema validation failed, proceeding with file discovery...")

        # Look for Abaco CSV files
        abaco_files = {
            "loan_data": self._find_abaco_file(["Loan Data", "Loan_Data"]),
            "payment_history": self._find_abaco_file(
                ["Historic Real Payment", "Payment_History"]
            ),
            "payment_schedule": self._find_abaco_file(
                ["Payment Schedule", "Payment_Schedule"]
            ),
        }

        loaded_data = {}
        total_loaded = 0

        for dataset_name, file_path in abaco_files.items():
            if file_path and file_path.exists():
                try:
                    df = pd.read_csv(file_path, encoding="utf-8")
                    loaded_data[dataset_name] = df
                    total_loaded += len(df)

                    expected_count = self.expected_records[dataset_name]
                    status = "✅" if len(df) == expected_count else "⚠️"
                    print(
                        f"{status} {dataset_name}: {len(df):,} records (expected: {expected_count:,})"
                    )

                    # Validate key columns for Abaco integration
                    self._validate_dataset_columns(df, dataset_name)

                except Exception as e:
                    print(f"❌ Error loading {dataset_name}: {e}")
            else:
                print(f"❌ File not found for {dataset_name}")

        # Final validation
        if total_loaded == self.expected_records["total"]:
            print(f"🎉 SUCCESS: {total_loaded:,} records loaded (EXACT MATCH)")
        else:
            print(
                f"⚠️  Loaded {total_loaded:,} records (expected {self.expected_records['total']:,})"
            )

        return loaded_data

    def _find_abaco_file(self, dataset_patterns: list) -> Optional[Path]:
        """Find Abaco CSV file by dataset name patterns."""
        for pattern in dataset_patterns:
            # Try multiple file naming patterns
            search_patterns = [
                f"*{pattern}*.csv",
                f"*Abaco*{pattern}*.csv",
                f"Abaco - Loan Tape_{pattern}_Table.csv",
                f"Abaco*{pattern.replace(' ', '_')}*.csv",
            ]

            for search_pattern in search_patterns:
                matches = list(self.data_dir.glob(search_pattern))
                if matches:
                    return matches[0]

        return None

    def _validate_dataset_columns(self, df: pd.DataFrame, dataset_name: str):
        """Validate dataset has required columns for Abaco processing."""

        required_columns = {
            "loan_data": [
                "Cliente",
                "Product Type",
                "Loan Currency",
                "Interest Rate APR",
                "Payment Frequency",
                "Outstanding Loan Value",
            ],
            "payment_history": [
                "Cliente",
                "True Total Payment",
                "True Payment Currency",
                "True Payment Status",
            ],
            "payment_schedule": ["Cliente", "Total Payment", "Currency"],
        }

        if dataset_name in required_columns:
            missing_cols = [
                col for col in required_columns[dataset_name] if col not in df.columns
            ]
            if missing_cols:
                print(f"⚠️  Missing columns in {dataset_name}: {missing_cols}")
            else:
                print(f"✅ Required columns validated for {dataset_name}")

                # Validate Abaco-specific values
                if dataset_name == "loan_data":
                    self._validate_abaco_loan_data(df)

    def _validate_abaco_loan_data(self, df: pd.DataFrame):
        """Validate Abaco loan data specifics."""

        # Validate USD currency
        if "Loan Currency" in df.columns:
            currencies = df["Loan Currency"].unique()
            if len(currencies) == 1 and currencies[0] == "USD":
                print("✅ USD currency validation passed")
            else:
                print(f"⚠️  Currency validation: {currencies}")

        # Validate factoring product
        if "Product Type" in df.columns:
            products = df["Product Type"].unique()
            if len(products) == 1 and products[0] == "factoring":
                print("✅ Factoring product validation passed")
            else:
                print(f"⚠️  Product validation: {products}")

        # Validate bullet payments
        if "Payment Frequency" in df.columns:
            frequencies = df["Payment Frequency"].unique()
            if len(frequencies) == 1 and frequencies[0] == "bullet":
                print("✅ Bullet payment validation passed")
            else:
                print(f"⚠️  Payment frequency validation: {frequencies}")

        # Validate interest rate range
        if "Interest Rate APR" in df.columns:
            rates = df["Interest Rate APR"].dropna()
            if not rates.empty:
                min_rate, max_rate = rates.min(), rates.max()
                if 0.2947 <= min_rate and max_rate <= 0.3699:
                    print(
                        f"✅ Interest rate range validated: {min_rate:.4f} - {max_rate:.4f}"
                    )
                else:
                    print(f"⚠️  Interest rate range: {min_rate:.4f} - {max_rate:.4f}")

        # Validate Spanish client names
        if "Cliente" in df.columns:
            spanish_companies = (
                df["Cliente"].str.contains("S.A. DE C.V.", na=False).sum()
            )
            total_clients = len(df["Cliente"].dropna())
            print(
                f"✅ Spanish companies identified: {spanish_companies}/{total_clients}"
            )

    def validate_schema(self) -> bool:
        """Validate data against Abaco schema."""

        for schema_path in self.schema_paths:
            if schema_path.exists():
                try:
                    with open(schema_path, "r") as f:
                        schema = json.load(f)

                    # Validate total record count
                    datasets = schema.get("datasets", {})
                    total_records = sum(
                        dataset.get("rows", 0)
                        for dataset in datasets.values()
                        if dataset.get("exists", False)
                    )

                    if total_records == 48853:
                        print(f"✅ Schema validation passed: {total_records:,} records")

                        # Validate Abaco integration flags
                        abaco_integration = schema.get("notes", {}).get(
                            "abaco_integration", {}
                        )
                        if (
                            abaco_integration.get("validation_status")
                            == "production_ready"
                        ):
                            print("✅ Production ready status confirmed")
                            return True
                    else:
                        print(f"⚠️  Schema record mismatch: {total_records:,}")
                        return False

                except Exception as e:
                    print(f"❌ Schema validation error: {e}")
                    continue

        print("⚠️  No valid schema found")
        return False
