"""
Commercial-View Data Loader - Abaco Integration
Handles loading and basic processing of portfolio data
Loads and validates 48,853 Abaco records based on validated schema structure
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Optional, List, Any

# Abaco integration constant expected by server_control.py
ABACO_RECORDS_EXPECTED = 48853


class DataLoaderError(Exception):
    """Exception raised for data loading errors."""

    pass


class DataLoader:
    """
    Data loader for Abaco loan tape processing.
    Handles exact schema structure: 16,205 + 16,443 + 16,205 = 48,853 records
    Provides both legacy methods and new Abaco-specific functionality.
    """

    def __init__(self, data_dir: str = "data", data_path: str = None, config_dir: str = "config"):
        """Initialize DataLoader with Abaco-specific configuration."""
        # Support both new and legacy initialization
        self.data_dir = Path(data_dir)
        self.data_path = Path(data_path) if data_path else Path("data/raw")
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
            "total": ABACO_RECORDS_EXPECTED,
        }

    # Legacy methods for backward compatibility
    def load_customer_data(self) -> Optional[pd.DataFrame]:
        """Load customer data - legacy method"""
        file_path = self.data_path / "Abaco - Loan Tape_Customer Data_Table"
        return self._load_excel_file(file_path, "customer_data")

    def load_loan_data(self) -> Optional[pd.DataFrame]:
        """Load loan data - legacy method"""
        file_path = self.data_path / "Abaco - Loan Tape_Loan Data_Table"
        return self._load_excel_file(file_path, "loan_data")

    def load_payment_history(self) -> Optional[pd.DataFrame]:
        """Load payment history - legacy method"""
        file_path = self.data_path / "Abaco - Loan Tape_Historic Real Payment_Table"
        return self._load_excel_file(file_path, "payment_history")

    def load_payment_schedule_old(self) -> Optional[pd.DataFrame]:
        """Load payment schedule - legacy method"""
        file_path = self.data_path / "Abaco - Loan Tape_Payment Schedule_Table"
        return self._load_excel_file(file_path, "payment_schedule")

    def load_payment_schedule(self) -> Optional[pd.DataFrame]:
        """Load payment schedule - wrapper for backward compatibility"""
        return self.load_payment_schedule_old()
    def _load_excel_file(
        self, file_path: Path, data_type: str
    ) -> Optional[pd.DataFrame]:
        """Helper method to load Excel files"""
        try:
            if file_path.exists():
                print(f"Loading {data_type} from {file_path}")
                df = pd.read_excel(file_path)
                print(f"Loaded {len(df)} rows for {data_type}")
                return df
            else:
                print(f"File not found: {file_path}")
                return None
        except Exception as e:
            print(f"Error loading {data_type}: {e}")
            return None

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all available datasets - legacy method"""
        datasets = {}

        loaders = {
            "customer_data": self.load_customer_data,
            "loan_data": self.load_loan_data,
            "payment_history": self.load_payment_history,
            "payment_schedule": self.load_payment_schedule_old,
        }

        for name, loader in loaders.items():
            data = loader()
            if data is not None:
                datasets[name] = data

        return datasets

    # New Abaco-specific methods
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


# Standalone functions for backwards compatibility with tests and pipeline
def load_customer_data() -> Optional[pd.DataFrame]:
    """Load customer data - standalone function"""
    loader = DataLoader()
    return loader.load_customer_data()


def load_loan_data() -> Optional[pd.DataFrame]:
    """Load loan data - standalone function"""
    loader = DataLoader()
    return loader.load_loan_data()


def load_payment_data() -> Optional[pd.DataFrame]:
    """Load payment data - standalone function"""
    loader = DataLoader()
    return loader.load_payment_history()


def load_schedule_data() -> Optional[pd.DataFrame]:
    """Load schedule data - standalone function (alias for load_payment_schedule)"""
    return load_payment_schedule()


def load_historic_real_payment() -> Optional[pd.DataFrame]:
    """Load historic real payment data - alias for payment history"""
    loader = DataLoader()
    return loader.load_payment_history()


def load_payment_schedule() -> Optional[pd.DataFrame]:
    """Load payment schedule data - standalone function"""
    loader = DataLoader()
    return loader.load_payment_schedule_old()


def load_collateral() -> Optional[pd.DataFrame]:
    """Load collateral data - placeholder function"""
    print("Collateral data not available in current dataset")
    return pd.DataFrame()  # Return empty DataFrame as placeholder


def load_abaco_data_standalone(data_type: str = "all") -> Dict[str, pd.DataFrame]:
    """Load Abaco data by type or all data - standalone function"""
    loader = DataLoader()
    
    if data_type == "all":
        return loader.load_all_data()
    elif data_type == "customer":
        result = loader.load_customer_data()
        return {"customer_data": result} if result is not None else {}
    elif data_type == "loan":
        result = loader.load_loan_data()
        return {"loan_data": result} if result is not None else {}
    elif data_type == "payment":
        result = loader.load_payment_history()
        return {"payment_history": result} if result is not None else {}
    elif data_type == "schedule":
        result = loader.load_payment_schedule_old()
        return {"payment_schedule": result} if result is not None else {}
    else:
        return {}


def load_abaco_dataset(data_type: str = "all") -> Dict[str, pd.DataFrame]:
    """Load Abaco dataset by type or all data (module-level function, avoids name collision)."""
    return load_abaco_data_standalone(data_type)
# Data validation functions
def validate_data_files() -> Dict[str, bool]:
    """Validate that all required data files exist"""
    data_path = Path("data/raw")
    required_files = [
        "Abaco - Loan Tape_Customer Data_Table",
        "Abaco - Loan Tape_Loan Data_Table", 
        "Abaco - Loan Tape_Historic Real Payment_Table",
        "Abaco - Loan Tape_Payment Schedule_Table"
    ]
    
    validation_results = {}
    for file in required_files:
        file_path = data_path / file
        validation_results[file] = file_path.exists()
    
    return validation_results


def get_data_summary() -> Dict[str, Any]:
    """Get summary of available data"""
    validation = validate_data_files()
    loader = DataLoader()
    
    summary = {
        "files_available": sum(validation.values()),
        "total_files": len(validation),
        "validation_details": validation,
        "data_path": str(loader.data_path)
    }
    
    return summary

