"""Utilities for loading pricing-related CSV data.

Installation (fixing "Import 'pandas' could not be resolved")
------------------------------------------------------------
1. Activate the virtual environment:
   $ source .venv/bin/activate

2. Install dependencies inside the venv:
   $ pip install pandas pydantic

3. (VS Code) Ensure the interpreter is the venv:
   - Command Palette → "Python: Select Interpreter" → pick .venv

Common mistakes to avoid
------------------------
- Using the system Python (e.g., /opt/homebrew/bin/python3) instead of the venv.
- Installing pandas outside the venv (then the module still isn't found inside it).
- Mixing `pip` and `pip3` across different interpreters.
- Forgetting to reload the window after switching interpreters in VS Code.

Quick checks
------------
- Verify you're on the venv's Python:
  ```bash
  which python
  python -c "import sys; print(sys.executable)"
  ```
  Expect a path ending in .venv/bin/python (macOS/Linux) or .venv\\Scripts\\python.exe (Windows).

- Confirm pandas is installed in this interpreter:
  ```bash
  python -c "import pandas as pd; print(pd.__version__)"
  pip show pandas
  ```
  pip show pandas → Location should point inside .venv.

- Double-check VS Code is using the venv:
  - Command Palette → Python: Select Interpreter → pick .venv
  - Then Developer: Reload Window
"""

from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from typing import Union, Optional, List, Dict, Any, Type, TypeVar, cast
import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel, Field, validator, root_validator
from datetime import date, datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Type variable for generic model types
T = TypeVar('T', bound=BaseModel)

# --------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------
PRICING_FILENAMES = {
    "loan_data": "loan_data.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "payment_schedule": "payment_schedule.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv",
}

# Column name mappings (raw CSV column name → model field name)
COLUMN_MAPPINGS = {
    # Loan Data
    "Customer ID": "CustomerID",
    "Application ID": "ApplicationID", 
    "Loan ID": "LoanID",
    "Product Type": "ProductType",
    "Disbursement Date": "DisbursementDate",
    "Disbursement Amount": "DisbursementAmount",
    "Origination Fee": "OriginationFee",
    "Origination Fee Taxes": "OriginationFeeTaxes",
    "Loan Currency": "LoanCurrency",
    "Interest Rate APR": "InterestRateAPR",
    "Term Unit": "TermUnit",
    "Payment Frequency": "PaymentFrequency",
    "Days in Default": "DaysInDefault",
    "Pledge To": "PledgeTo",
    "Pledge Date": "PledgeDate",
    "Loan Status": "LoanStatus",
    "Outstanding Loan Value": "OutstandingLoanValue",
    "New Loan ID": "NewLoanID",
    "New Loan Date": "NewLoanDate",
    "Old Loan ID": "OldLoanID",
    "Recovery Date": "RecoveryDate",
    "Recovery Value": "RecoveryValue",
    
    # Historic Real Payment
    "True Payment Date": "TruePaymentDate",
    "True Devolution": "TrueDevolution",
    "True Total Payment": "TrueTotalPayment",
    "True Payment Currency": "TruePaymentCurrency",
    "True Principal Payment": "TruePrincipalPayment",
    "True Interest Payment": "TrueInterestPayment",
    "True Fee Payment": "TrueFeePayment",
    "True Other Payment": "TrueOtherPayment",
    "True Tax Payment": "TrueTaxPayment",
    "True Fee Tax Payment": "TrueFeeTaxPayment",
    "True Rabates": "TrueRabates",
    "True Outstanding Loan Value": "TrueOutstandingLoanValue",
    "True Payment Status": "TruePaymentStatus",
    
    # Payment Schedule
    "Payment Date": "PaymentDate",
    "Total Payment": "TotalPayment",
    "Currency": "Currency",
    "Principal Payment": "PrincipalPayment",
    "Interest Payment": "InterestPayment",
    "Fee Payment": "FeePayment",
    "Other Payment": "OtherPayment",
    "Tax Payment": "TaxPayment",
    "All Rebates": "AllRebates",
}

# --------------------------------------------------------------------
# Data Models
# --------------------------------------------------------------------
class LoanData(BaseModel):
    """Schema for validating loan-level data records.
    
    Corresponds to the Loan Data dataset in the Abaco schema.
    """
    Company: str = Field(..., description="Name of the company owning the loan portfolio.")
    CustomerID: str = Field(..., description="Unique identifier for the customer.")
    Cliente: str = Field(..., description="Customer's legal or trade name.")
    Pagador: str = Field(..., description="Entity responsible for loan repayment.")
    ApplicationID: str = Field(..., description="Unique identifier for the loan application.")
    LoanID: str = Field(..., description="Unique loan identifier.")
    ProductType: str = Field(..., description="Type of product (e.g., factoring).")
    DisbursementDate: date = Field(..., description="Loan disbursement date.")
    TPV: float = Field(..., ge=0, description="Total purchase volume or equivalent exposure.")
    DisbursementAmount: float = Field(..., ge=0, description="Principal amount disbursed.")
    OriginationFee: float = Field(..., ge=0, description="Origination fee charged on the loan.")
    OriginationFeeTaxes: float = Field(..., ge=0, description="Taxes applied to origination fees.")
    LoanCurrency: str = Field(..., description="Currency code (e.g., USD).")
    InterestRateAPR: float = Field(..., ge=0, description="Annual percentage rate of interest.")
    Term: int = Field(..., ge=1, description="Loan term length.")
    TermUnit: str = Field(..., description="Unit of measurement for the term (e.g., days).")
    PaymentFrequency: str = Field(..., description="Frequency of loan payments (e.g., bullet).")
    DaysInDefault: int = Field(0, ge=0, description="Number of days the loan is in default.")
    PledgeTo: Optional[float] = Field(None, description="Pledge amount to another entity.")
    PledgeDate: Optional[date] = Field(None, description="Date of pledge.")
    LoanStatus: str = Field(..., description="Current status of the loan (e.g., Current, Complete, Default).")
    OutstandingLoanValue: float = Field(..., ge=0, description="Current outstanding loan value.")
    Other: Optional[float] = Field(None, description="Other related amounts.")
    NewLoanID: Optional[str] = Field(None, description="ID for a refinanced loan.")
    NewLoanDate: Optional[date] = Field(None, description="Date of refinancing.")
    OldLoanID: Optional[str] = Field(None, description="Original loan ID if refinanced.")
    RecoveryDate: Optional[date] = Field(None, description="Date of recovery for defaulted loans.")
    RecoveryValue: Optional[float] = Field(None, ge=0, description="Amount recovered from defaulted loans.")
    Segment: Optional[str] = Field(None, description="Customer segment classification.")
    RevenueBand: Optional[str] = Field(None, description="Revenue band for the customer.")
    LineaCredito: Optional[float] = Field(None, ge=0, description="Credit line associated with the customer.")
    Collateral: Optional[str] = Field(None, description="Collateral type or ID linked to the loan.")

    @validator("LoanCurrency")
    def currency_uppercase(cls, v):
        return v.upper() if v else v

    @validator("DisbursementDate")
    def validate_disbursement_date(cls, v):
        if v and v > date.today():
            raise ValueError("Disbursement date cannot be in the future.")
        return v
    
    @validator("ProductType")
    def validate_product_type(cls, v):
        return v.lower() if v else v
    
    class Config:
        extra = "ignore"  # Ignore extra fields not in the model
        anystr_strip_whitespace = True  # Strip whitespace from string values

class HistoricRealPayment(BaseModel):
    """Schema for validating historic real payment records.
    
    Corresponds to the Historic Real Payment dataset in the Abaco schema.
    """
    Company: str = Field(..., description="Name of the company owning the loan.")
    CustomerID: str = Field(..., description="Unique identifier for the customer.")
    Cliente: str = Field(..., description="Customer's legal or trade name.")
    Pagador: str = Field(..., description="Entity responsible for loan repayment.")
    LoanID: str = Field(..., description="Unique loan identifier.")
    TruePaymentDate: date = Field(..., description="Actual date when payment was received.")
    TrueDevolution: float = Field(..., ge=0, description="Amount returned to the customer.")
    TrueTotalPayment: float = Field(..., ge=0, description="Total payment amount received.")
    TruePaymentCurrency: str = Field(..., description="Currency of the payment.")
    TruePrincipalPayment: float = Field(..., ge=0, description="Portion of payment allocated to principal.")
    TrueInterestPayment: float = Field(..., ge=0, description="Portion of payment allocated to interest.")
    TrueFeePayment: float = Field(..., ge=0, description="Portion of payment allocated to fees.")
    TrueOtherPayment: Optional[float] = Field(None, description="Portion of payment allocated to other categories.")
    TrueTaxPayment: float = Field(..., ge=0, description="Portion of payment allocated to taxes.")
    TrueFeeTaxPayment: float = Field(..., ge=0, description="Portion of payment allocated to fee taxes.")
    TrueRabates: int = Field(..., ge=0, description="Number of rebates applied.")
    TrueOutstandingLoanValue: float = Field(..., ge=0, description="Remaining loan value after payment.")
    TruePaymentStatus: str = Field(..., description="Status of the payment (e.g., Late, On Time, Prepayment).")

    @validator("TruePaymentCurrency")
    def currency_uppercase(cls, v):
        return v.upper() if v else v
    
    @validator("TruePaymentDate")
    def validate_payment_date(cls, v):
        if v and v > date.today():
            raise ValueError("Payment date cannot be in the future.")
        return v
    
    class Config:
        extra = "ignore"
        anystr_strip_whitespace = True

class PaymentSchedule(BaseModel):
    """Schema for validating payment schedule records.
    
    Corresponds to the Payment Schedule dataset in the Abaco schema.
    """
    Company: str = Field(..., description="Name of the company owning the loan.")
    CustomerID: str = Field(..., description="Unique identifier for the customer.")
    Cliente: str = Field(..., description="Customer's legal or trade name.")
    Pagador: str = Field(..., description="Entity responsible for loan repayment.")
    LoanID: str = Field(..., description="Unique loan identifier.")
    PaymentDate: date = Field(..., description="Scheduled date for the payment.")
    TPV: float = Field(..., ge=0, description="Total purchase volume related to this payment.")
    TotalPayment: float = Field(..., ge=0, description="Total scheduled payment amount.")
    Currency: str = Field(..., description="Currency of the payment.")
    PrincipalPayment: float = Field(..., ge=0, description="Portion of payment allocated to principal.")
    InterestPayment: float = Field(..., ge=0, description="Portion of payment allocated to interest.")
    FeePayment: float = Field(..., ge=0, description="Portion of payment allocated to fees.")
    OtherPayment: Optional[float] = Field(None, description="Portion of payment allocated to other categories.")
    TaxPayment: float = Field(..., ge=0, description="Portion of payment allocated to taxes.")
    AllRebates: Optional[float] = Field(None, description="Total rebates applied to this payment.")
    OutstandingLoanValue: int = Field(..., ge=0, description="Projected outstanding loan value after this payment.")

    @validator("Currency")
    def currency_uppercase(cls, v):
        return v.upper() if v else v
    
    @validator("PaymentDate")
    def validate_future_date(cls, v):
        # For payment schedules, future dates are valid
        return v
    
    @root_validator(pre=False)
    def validate_payment_components(cls, values):
        """Validate that payment components sum up to the total payment."""
        if all(key in values for key in ['PrincipalPayment', 'InterestPayment', 'FeePayment', 'TaxPayment', 'TotalPayment']):
            components_sum = values['PrincipalPayment'] + values['InterestPayment'] + values['FeePayment'] + values['TaxPayment']
            other = values.get('OtherPayment', 0) or 0
            components_sum += other
            
            # Allow for small floating point differences
            if abs(components_sum - values['TotalPayment']) > 0.01:
                logger.warning(
                    f"Payment components don't sum to total: {components_sum} vs {values['TotalPayment']}"
                    f" (Loan ID: {values.get('LoanID', 'unknown')})"
                )
        return values
    
    class Config:
        extra = "ignore"
        anystr_strip_whitespace = True

class CustomerData(BaseModel):
    """Schema for validating customer data records."""
    business_year_founded: Optional[int] = Field(None, description="Year the business was founded.")
    equifax_score: Optional[str] = Field(None, description="Equifax credit score for the customer.")
    category: Optional[str] = Field(None, description="Business category.")
    credit_line_category: Optional[str] = Field(None, description="Credit line category.")
    subcategory: Optional[str] = Field(None, description="Business subcategory.")
    credit_line_subcategory: Optional[str] = Field(None, description="Credit line subcategory.")
    industry: Optional[str] = Field(None, description="Industry the business operates in.")
    birth_year: Optional[int] = Field(None, description="Year of birth for individual customers.")
    occupation: Optional[str] = Field(None, description="Customer's occupation.")
    client_type: Optional[str] = Field(None, description="Type of client.")
    location_city: Optional[str] = Field(None, description="Customer's city location.")
    location_state_province: Optional[str] = Field(None, description="Customer's state/province location.")
    location_country: Optional[str] = Field(None, description="Customer's country location.")
    customer_id: str = Field(..., description="Unique identifier for the customer.")
    customer_name: str = Field(..., description="Customer's name.")
    
    class Config:
        extra = "ignore"
        anystr_strip_whitespace = True

class Collateral(BaseModel):
    """Schema for validating collateral records."""
    customer_id: str = Field(..., description="Unique identifier for the customer.")
    customer_name: str = Field(..., description="Customer's name.")
    loan_id: str = Field(..., description="Loan ID associated with this collateral.")
    collateral_id: str = Field(..., description="Unique identifier for the collateral.")
    collateral_original_value: float = Field(..., ge=0, description="Original valuation of the collateral.")
    collateral_current_value: float = Field(..., ge=0, description="Current valuation of the collateral.")
    
    class Config:
        extra = "ignore"
        anystr_strip_whitespace = True

class SchemaInfo(BaseModel):
    """Schema metadata information loaded from JSON schema file."""
    datasets: Dict[str, Any]
    notes: Dict[str, Any]
    
    class Config:
        extra = "ignore"

# --------------------------------------------------------------------
# Schema Management
# --------------------------------------------------------------------
def load_schema(schema_path: Optional[Union[str, Path]] = None) -> SchemaInfo:
    """Load the JSON schema file containing dataset information.
    
    Args:
        schema_path: Path to the JSON schema file. If None, looks for the file
                     in predefined locations.
    
    Returns:
        SchemaInfo object containing dataset metadata
    """
    if schema_path is None:
        # Try common locations
        possible_paths = [
            Path("schema/abaco_schema.json"),
            Path("data/schema/abaco_schema.json"),
            Path(__file__).parent.parent / "schema" / "abaco_schema.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                schema_path = path
                break
    
    if schema_path is None or not Path(schema_path).exists():
        logger.warning("Schema file not found. Using default schema definitions.")
        return SchemaInfo(datasets={}, notes={})
    
    with open(schema_path, 'r') as f:
        schema_data = json.load(f)
    
    return SchemaInfo(**schema_data)

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def _resolve_base_path(path: Optional[Union[str, Path]] = None) -> Path:
    """Resolve the base directory where the CSV files are located."""
    base = Path(path or os.getenv("COMMERCIAL_VIEW_DATA_PATH", "data")).expanduser()
    if not base.exists():
        raise FileNotFoundError(f"Base path not found: {base}")
    return base

def _read_csv(base_path: Path, filename: str) -> DataFrame:
    """Read a CSV file from the specified base path."""
    file_path = base_path / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")
    return pd.read_csv(file_path)

def _normalize_dataframe(df: DataFrame) -> DataFrame:
    """Normalize DataFrame column names to match model field names."""
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Rename columns according to the mapping
    rename_dict = {k: v for k, v in COLUMN_MAPPINGS.items() if k in df.columns}
    if rename_dict:
        df = df.rename(columns=rename_dict)

    return df

def _convert_date_columns(df: DataFrame, date_columns: List[str]) -> DataFrame:
    """Convert string date columns to datetime.date objects."""
    df = df.copy()
    for col in date_columns:
        if col in df.columns and pd.notna(df[col]).any():
            try:
                df[col] = pd.to_datetime(df[col]).dt.date
            except Exception as e:
                logger.warning(f"Failed to convert {col} to date: {e}")
    return df

def _validate_dataframe(
    df: DataFrame, 
    model_class: Type[T],
    include_failures: bool = False
) -> List[T]:
    """Validate DataFrame rows against a Pydantic model.
    
    Args:
        df: DataFrame to validate
        model_class: Pydantic model class to validate against
        include_failures: If True, include records that fail validation with errors
                          If False, only include valid records
    
    Returns:
        List of validated model instances
    """
    validated_records = []
    total_records = len(df)
    failure_count = 0
    
    for i, row in df.iterrows():
        try:
            record = model_class(**row.to_dict())
            validated_records.append(record)
        except Exception as e:
            failure_count += 1
            record_id = row.get('LoanID', row.get('CustomerID', f"row {i}"))
            logger.warning(f"Validation error in {record_id}: {e}")
            if include_failures:
                # If requested, include the record anyway with validation errors
                try:
                    # Use exclude_unset to avoid validation
                    record = model_class.construct(**row.to_dict())
                    setattr(record, "_validation_errors", str(e))
                    validated_records.append(record)
                except Exception as e2:
                    logger.error(f"Failed to construct model for {record_id}: {e2}")
    
    if failure_count > 0:
        logger.info(f"Validated {total_records - failure_count}/{total_records} records successfully")
    
    return validated_records

# --------------------------------------------------------------------
# Public Loaders
# --------------------------------------------------------------------
def load_loan_data(
    path: Optional[Union[str, Path]] = None,
    validate: bool = False,
    include_failures: bool = False
) -> Union[DataFrame, List[LoanData]]:
    """Load the loan data CSV.
    
    Args:
        path: Path to a file or directory. If None, uses the COMMERCIAL_VIEW_DATA_PATH environment variable
              or defaults to the 'data' directory.
        validate: If True, returns a list of validated model objects instead of DataFrame
        include_failures: If True, include records that fail validation
        
    Returns:
        DataFrame or list of validated model objects
    
    Raises:
        FileNotFoundError: If no suitable CSV file is found
    """
    base_path = _resolve_base_path(path)
    df = _read_csv(base_path, PRICING_FILENAMES["loan_data"])
    df = _normalize_dataframe(df)

    date_columns = ['DisbursementDate', 'PledgeDate', 'NewLoanDate', 'RecoveryDate']
    df = _convert_date_columns(df, date_columns)

    # Validation logic would go here if validate=True

    return df

def load_historic_real_payment(
    path: Optional[Union[str, Path]] = None,
    validate: bool = False,
    include_failures: bool = False
) -> Union[DataFrame, List[HistoricRealPayment]]:
    """Load the historic real payment CSV.
    
    Args:
        path: Optional path to data directory
        validate: If True, returns a list of validated HistoricRealPayment objects
        include_failures: If True, include records that fail validation
        
    Returns:
        DataFrame or list of validated HistoricRealPayment objects
    """
    df = _read_csv(_resolve_base_path(path), PRICING_FILENAMES["historic_real_payment"])
    df = _normalize_dataframe(df)
    
    date_columns = ['TruePaymentDate']
    df = _convert_date_columns(df, date_columns)

    return df

def load_payment_schedule(
    path: Optional[Union[str, Path]] = None,
    validate: bool = False,
    include_failures: bool = False
) -> Union[DataFrame, List[PaymentSchedule]]:
    """Load the payment schedule CSV.
    
    Args:
        path: Optional path to data directory
        validate: If True, returns a list of validated PaymentSchedule objects
        include_failures: If True, include records that fail validation
        
    Returns:
        DataFrame or list of validated PaymentSchedule objects
    """
    df = _read_csv(_resolve_base_path(path), PRICING_FILENAMES["payment_schedule"])
    df = _normalize_dataframe(df)
    
    date_columns = ['PaymentDate']
    df = _convert_date_columns(df, date_columns)

    return df

def load_customer_data(
    path: Optional[Union[str, Path]] = None,
    validate: bool = False,
    include_failures: bool = False
) -> Union[DataFrame, List[CustomerData]]:
    """Load the customer data CSV.
    
    Args:
        path: Optional path to data directory
        validate: If True, returns a list of validated CustomerData objects
        include_failures: If True, include records that fail validation
        
    Returns:
        DataFrame or list of validated CustomerData objects
    """
    df = _read_csv(_resolve_base_path(path), PRICING_FILENAMES["customer_data"])
    
    # Customer data may have different column naming convention
    if validate:
        return _validate_dataframe(df, CustomerData, include_failures)
    
    return df

def load_collateral(
    path: Optional[Union[str, Path]] = None,
    validate: bool = False,
    include_failures: bool = False
) -> Union[DataFrame, List[Collateral]]:
    """Load the collateral CSV.
    
    Args:
        path: Optional path to data directory
        validate: If True, returns a list of validated Collateral objects
        include_failures: If True, include records that fail validation
        
    Returns:
        DataFrame or list of validated Collateral objects
    """
    df = _read_csv(_resolve_base_path(path), PRICING_FILENAMES["collateral"])
    
    # Collateral may have different column naming convention
    if validate:
        return _validate_dataframe(df, Collateral, include_failures)
    
    return df

# --------------------------------------------------------------------
# DataLoader Class
# --------------------------------------------------------------------
class DataLoader:
    """Class for loading and managing data from CSV files with validation."""
    
    def __init__(
        self, 
        base_path: Optional[Union[str, Path]] = None
    ):
        """Initialize with optional base path.
        
        Args:
            base_path: Base directory for data files or direct path to a CSV file
        """
        self.base_path = base_path or os.getenv("COMMERCIAL_VIEW_DATA_PATH", "data")
    
    def load_loan_data(
        self, validate: bool = False, include_failures: bool = False
    ) -> Union[DataFrame, List[LoanData]]:
        """Load loan data using instance base path."""
        return load_loan_data(self.base_path, validate, include_failures)

    def load_historic_real_payment(
        self, validate: bool = False, include_failures: bool = False
    ) -> Union[DataFrame, List[HistoricRealPayment]]:
        """Load historic real payment data using instance base path."""
        return load_historic_real_payment(self.base_path, validate, include_failures)

    def load_payment_schedule(
        self, validate: bool = False, include_failures: bool = False
    ) -> Union[DataFrame, List[PaymentSchedule]]:
        """Load payment schedule data using instance base path."""
        return load_payment_schedule(self.base_path, validate, include_failures)

    def load_customer_data(
        self, validate: bool = False, include_failures: bool = False
    ) -> Union[DataFrame, List[CustomerData]]:
        """Load customer data using instance base path."""
        return load_customer_data(self.base_path, validate, include_failures)

    def load_collateral(
        self, validate: bool = False, include_failures: bool = False
    ) -> Union[DataFrame, List[Collateral]]:
        """Load collateral data using instance base path."""
        return load_collateral(self.base_path, validate, include_failures)
    
    def load_all(self, validate: bool = False) -> Dict[str, Union[DataFrame, List[Union[LoanData, HistoricRealPayment, PaymentSchedule, CustomerData, Collateral]]]]:
        """Load all available datasets.
        
        Args:
            validate: If True, validates the data against models
            
        Returns:
            Dictionary mapping dataset names to data
        """
        result = {}
        
        # Try to load each dataset, ignoring FileNotFoundError
        try:
            result['loan_data'] = self.load_loan_data(validate=validate)
        except FileNotFoundError:
            logger.warning("Loan data file not found")
        
        try:
            result['historic_real_payment'] = self.load_historic_real_payment(validate=validate)
        except FileNotFoundError:
            logger.warning("Historic real payment file not found")
        
        try:
            result['payment_schedule'] = self.load_payment_schedule(validate=validate)
        except FileNotFoundError:
            logger.warning("Payment schedule file not found")
        
        try:
            result['customer_data'] = self.load_customer_data(validate=validate)
        except FileNotFoundError:
            logger.warning("Customer data file not found")
        
        try:
            result['collateral'] = self.load_collateral(validate=validate)
        except FileNotFoundError:
            logger.warning("Collateral file not found")
        
        return result


# Example usage
if __name__ == "__main__":
    # Configure logging for the example
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Example of loading with DataLoader class
        loader = DataLoader()
        
        # Load loan data without validation (returns DataFrame)
        loan_df = loader.load_loan_data()
        print(f"Loaded {len(loan_df)} loan records as DataFrame")
        
        # Load loan data with validation (returns list of LoanData objects)
        loan_data = loader.load_loan_data(validate=True)
        if isinstance(loan_data, list):
            print(f"Validated {len(loan_data)} loan records")
            
            # Print sample data
            if loan_data:
                sample = loan_data[0]
                print(f"Sample loan: ID={sample.LoanID}, Currency={sample.LoanCurrency}, Status={sample.LoanStatus}")
                
        # Try to load all available datasets
        all_data = loader.load_all(validate=False)
        print(f"Loaded {len(all_data)} datasets")
        for name, data in all_data.items():
            if isinstance(data, pd.DataFrame):
                print(f"  {name}: {len(data)} records")
            else:
                print(f"  {name}: {len(data)} validated records")
                
    except Exception as e:
        logger.error(f"Error in example: {e}", exc_info=True)
        print(f"Data loading example failed: {e}")
        print("Make sure you have the required CSV files in your data directory")

__all__ = [
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral",
    "LoanData",
    "HistoricRealPayment", 
    "PaymentSchedule",
    "CustomerData",
    "Collateral",
    "DataLoader",
    "load_schema",
    "SchemaInfo"
]

from fastapi import APIRouter

router = APIRouter()

# ...existing routes...

@router.get("/executive-summary")
def executive_summary():
    return {
        "portfolio_overview": {},  # existing
        "risk_indicators": {},     # added as requested
    }

# ...existing code...