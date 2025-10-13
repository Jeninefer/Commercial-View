"""
Abaco Schema Integration Module

Provides comprehensive schema validation and integration for the Abaco loan tape data
based on the autodetected schema JSON file.
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

# Column name constants (from your schema)
DAYS_IN_DEFAULT_COLUMN = "Days in Default"
INTEREST_RATE_APR_COLUMN = "Interest Rate APR"
OUTSTANDING_LOAN_VALUE_COLUMN = "Outstanding Loan Value"
LOAN_CURRENCY_COLUMN = "Loan Currency"
PRODUCT_TYPE_COLUMN = "Product Type"
CUSTOMER_ID_COLUMN = "Customer ID"
LOAN_ID_COLUMN = "Loan ID"
DISBURSEMENT_DATE_COLUMN = "Disbursement Date"
DISBURSEMENT_AMOUNT_COLUMN = "Disbursement Amount"
TRUE_PAYMENT_DATE_COLUMN = "True Payment Date"
CLIENTE_COLUMN = "Cliente"
PAYMENT_FREQUENCY_COLUMN = "Payment Frequency"

# Business constants
USD_CURRENCY = "USD"
FACTORING_PRODUCT = "factoring"
BULLET_FREQUENCY = "bullet"
ABACO_TECHNOLOGIES = "Abaco Technologies"
ABACO_FINANCIAL = "Abaco Financial"

# Expected values
EXPECTED_TOTAL_RECORDS = 48853
EXPECTED_LOAN_RECORDS = 16205
EXPECTED_PAYMENT_RECORDS = 16443
EXPECTED_SCHEDULE_RECORDS = 16205
EXPECTED_PORTFOLIO_VALUE = 208192588.65

# Constants to eliminate code duplication (addressing SonarLint issues)
DATA_LOADER_NOT_AVAILABLE_MSG = "Data loader not available"
ABACO_SCHEMA_FILENAME = "abaco_schema_autodetected.json"

def validate_schema(schema_data: Dict[str, Any]) -> bool:
    """
    Validate Abaco schema structure and content.
    
    Args:
        schema_data: Dictionary containing schema information
        
    Returns:
        True if schema is valid, False otherwise
    """
    try:
        # Check for required datasets
        if 'datasets' not in schema_data:
            logger.error("Missing 'datasets' key in schema")
            return False
        
        datasets = schema_data['datasets']
        required_datasets = ['Loan Data', 'Historic Real Payment', 'Payment Schedule']
        
        for dataset_name in required_datasets:
            if dataset_name not in datasets:
                logger.error(f"Missing required dataset: {dataset_name}")
                return False
        
        # Validate record counts
        loan_data = datasets.get('Loan Data', {})
        payment_data = datasets.get('Historic Real Payment', {})
        schedule_data = datasets.get('Payment Schedule', {})
        
        if loan_data.get('rows') != EXPECTED_LOAN_RECORDS:
            logger.warning(f"Unexpected loan record count: {loan_data.get('rows')}")
        
        if payment_data.get('rows') != EXPECTED_PAYMENT_RECORDS:
            logger.warning(f"Unexpected payment record count: {payment_data.get('rows')}")
        
        if schedule_data.get('rows') != EXPECTED_SCHEDULE_RECORDS:
            logger.warning(f"Unexpected schedule record count: {schedule_data.get('rows')}")
        
        logger.info("✅ Schema validation passed")
        return True
    
    except Exception as e:
        logger.error(f"Schema validation error: {e}")
        return False


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """
    Load Abaco schema from JSON file.
    
    Args:
        schema_path: Path to schema JSON file
        
    Returns:
        Schema dictionary
    """
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading schema: {e}")
        raise


def get_column_names() -> Dict[str, str]:
    """Get dictionary of all column name constants."""
    return {
        'days_in_default': DAYS_IN_DEFAULT_COLUMN,
        'interest_rate_apr': INTEREST_RATE_APR_COLUMN,
        'outstanding_loan_value': OUTSTANDING_LOAN_VALUE_COLUMN,
        'loan_currency': LOAN_CURRENCY_COLUMN,
        'product_type': PRODUCT_TYPE_COLUMN,
        'customer_id': CUSTOMER_ID_COLUMN,
        'loan_id': LOAN_ID_COLUMN,
        'disbursement_date': DISBURSEMENT_DATE_COLUMN,
        'disbursement_amount': DISBURSEMENT_AMOUNT_COLUMN,
        'true_payment_date': TRUE_PAYMENT_DATE_COLUMN,
        'cliente': CLIENTE_COLUMN,
        'payment_frequency': PAYMENT_FREQUENCY_COLUMN
    }

class AbacoSchemaManager:
    """
    Manages Abaco schema validation and integration using the autodetected schema.
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize schema manager.
        
        Args:
            schema_path: Path to the abaco_schema_autodetected.json file
        """
        self.schema = {}
        self.schema_path = schema_path
        
        if schema_path and Path(schema_path).exists():
            self.load_schema(schema_path)
        else:
            logger.warning(f"Schema file not found: {schema_path}")
    
    def load_schema(self, schema_path: str) -> bool:
        """Load the Abaco schema from JSON file."""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            logger.info(f"✅ Loaded Abaco schema from {schema_path}")
            logger.info(f"📊 Schema contains {len(self.schema.get('datasets', {}))} datasets")
            
            # Log dataset summaries
            for dataset_name, dataset_info in self.schema.get('datasets', {}).items():
                if dataset_info.get('exists', False):
                    rows = dataset_info.get('rows', 0)
                    cols = len(dataset_info.get('columns', []))
                    logger.info(f"  - {dataset_name}: {rows:,} rows, {cols} columns")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            return False
    
    def get_dataset_schema(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Get schema information for a specific dataset."""
        return self.schema.get('datasets', {}).get(dataset_name)
    
    def get_expected_columns(self, dataset_name: str) -> List[Dict[str, Any]]:
        """Get expected columns for a dataset."""
        dataset_schema = self.get_dataset_schema(dataset_name)
        if not dataset_schema:
            return []
        
        return dataset_schema.get('columns', [])
    
    def validate_dataframe_structure(self, df: pd.DataFrame, dataset_name: str) -> Tuple[bool, List[str]]:
        """
        Validate DataFrame structure against schema.
        
        Args:
            df: DataFrame to validate
            dataset_name: Name of the dataset in schema
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Get expected schema
        expected_columns = self.get_expected_columns(dataset_name)
        if not expected_columns:
            issues.append(f"No schema found for dataset: {dataset_name}")
            return False, issues
        
        # Create lookup for expected columns
        expected_col_info = {col['name']: col for col in expected_columns}
        
        # Check for missing required columns (non_null > 0)
        required_columns = [
            col['name'] for col in expected_columns 
            if col.get('non_null', 0) > 0
        ]
        
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            issues.append(f"Missing required columns: {missing_required}")
        
        # Check for unexpected columns
        unexpected_columns = [col for col in df.columns if col not in expected_col_info]
        if unexpected_columns:
            issues.append(f"Unexpected columns found: {unexpected_columns}")
        
        # Validate data types for existing columns
        for col_name in df.columns:
            if col_name in expected_col_info:
                expected_info = expected_col_info[col_name]
                actual_dtype = str(df[col_name].dtype)
                expected_dtype = expected_info.get('dtype', '')
                
                # Type compatibility check
                if not self._is_dtype_compatible(actual_dtype, expected_dtype):
                    issues.append(f"Column '{col_name}': expected {expected_dtype}, got {actual_dtype}")
        
        # Check row count expectations
        dataset_schema = self.get_dataset_schema(dataset_name)
        if dataset_schema and 'rows' in dataset_schema:
            expected_rows = dataset_schema['rows']
            actual_rows = len(df)
            
            # Allow some tolerance for row count differences
            tolerance = 0.05  # 5% tolerance
            if abs(actual_rows - expected_rows) / expected_rows > tolerance:
                issues.append(f"Row count mismatch: expected ~{expected_rows:,}, got {actual_rows:,}")
        
        return len(issues) == 0, issues
    
    def _is_dtype_compatible(self, actual_dtype: str, expected_dtype: str) -> bool:
        """Check if actual data type is compatible with expected type."""
        type_mappings = {
            'string': ['object', 'str', 'string'],
            'float': ['float64', 'float32', 'int64', 'int32'],  # Allow int->float conversion
            'int': ['int64', 'int32', 'int16', 'int8'],
            'datetime': ['datetime64[ns]', 'object']  # object can contain datetime strings
        }
        
        if expected_dtype in type_mappings:
            return any(dtype in actual_dtype.lower() for dtype in type_mappings[expected_dtype])
        
        return True  # If we don't know the expected type, assume compatible
    
    def get_sample_values(self, dataset_name: str, column_name: str) -> List[str]:
        """Get sample values for a specific column."""
        expected_columns = self.get_expected_columns(dataset_name)
        
        for col in expected_columns:
            if col['name'] == column_name:
                return col.get('sample_values', [])
        
        return []
    
    def generate_schema_report(self) -> Dict[str, Any]:
        """Generate comprehensive schema report."""
        report = {
            'generation_time': datetime.now().isoformat(),
            'schema_summary': {
                'total_datasets': len(self.schema.get('datasets', {})),
                'available_datasets': 0,
                'total_columns': 0,
                'total_rows': 0
            },
            'datasets': {},
            'schema_metadata': self.schema.get('notes', {})
        }
        
        for dataset_name, dataset_info in self.schema.get('datasets', {}).items():
            if dataset_info.get('exists', False):
                report['schema_summary']['available_datasets'] += 1
                rows = dataset_info.get('rows', 0)
                cols = len(dataset_info.get('columns', []))
                
                report['schema_summary']['total_rows'] += rows
                report['schema_summary']['total_columns'] += cols
                
                # Dataset details
                report['datasets'][dataset_name] = {
                    'status': dataset_info.get('status', 'unknown'),
                    'rows': rows,
                    'columns': cols,
                    'path': dataset_info.get('path', ''),
                    'column_summary': self._analyze_columns(dataset_info.get('columns', []))
                }
        
        return report
    
    def _analyze_columns(self, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze column information for summary."""
        summary = {
            'data_types': {},
            'null_columns': [],
            'required_columns': [],
            'datetime_columns': []
        }
        
        for col in columns:
            # Count data types
            dtype = col.get('dtype', 'unknown')
            summary['data_types'][dtype] = summary['data_types'].get(dtype, 0) + 1
            
            # Identify null columns
            if col.get('nulls', 0) == col.get('non_null', 0) + col.get('nulls', 0):
                summary['null_columns'].append(col['name'])
            
            # Identify required columns
            if col.get('non_null', 0) > 0:
                summary['required_columns'].append(col['name'])
            
            # Identify datetime columns
            if col.get('coerced_dtype') == 'datetime':
                summary['datetime_columns'].append(col['name'])
        
        return summary
    
    def create_column_mapping_config(self, output_path: str) -> bool:
        """Create YAML column mapping configuration from schema."""
        try:
            import yaml
            
            config = {
                'schema_info': {
                    'generated_from': ABACO_SCHEMA_FILENAME,
                    'generation_time': datetime.now().isoformat(),
                    'total_datasets': len([d for d in self.schema.get('datasets', {}).values() if d.get('exists')])
                }
            }
            
            # Generate mappings for each dataset
            for dataset_name, dataset_info in self.schema.get('datasets', {}).items():
                if not dataset_info.get('exists', False):
                    continue
                
                # Convert dataset name to config key
                config_key = dataset_name.lower().replace(' ', '_')
                config[config_key] = {}
                
                # Map each column
                for col in dataset_info.get('columns', []):
                    col_name = col['name']
                    # Create standardized field name
                    field_name = col_name.lower().replace(' ', '_').replace('true_', '').replace('id', '_id')
                    
                    # Skip null columns
                    if col.get('nulls', 0) > 0 and col.get('non_null', 0) == 0:
                        continue
                    
                    config[config_key][field_name] = col_name
            
            # Write configuration file
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"✅ Created column mapping configuration: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating column mapping config: {e}")
            return False

# Integration function for DataLoader
def integrate_abaco_schema(data_loader_class):
    """Decorator to integrate Abaco schema validation into DataLoader."""
    
    original_init = data_loader_class.__init__
    
    def new_init(self, config_dir=None, data_dir=None, schema_path=None):
        # Call original init
        original_init(self, config_dir, data_dir)
        
        # Add schema manager
        if not schema_path:
            # Try to find schema in Downloads or config directory
            potential_paths = [
                str(Path.home() / 'Downloads' / ABACO_SCHEMA_FILENAME),
                str(Path(self.config_dir) / ABACO_SCHEMA_FILENAME)
            ]
            for path in potential_paths:
                if Path(path).exists():
                    schema_path = path
                    break
        
        self.schema_manager = AbacoSchemaManager(schema_path)
    
    data_loader_class.__init__ = new_init
    return data_loader_class

# Export constants for use in other modules
__all__ = [
    'AbacoSchemaManager',
    'integrate_abaco_schema',
    'CUSTOMER_ID_COLUMN',
    'DAYS_IN_DEFAULT_COLUMN', 
    'OUTSTANDING_LOAN_VALUE_COLUMN',
    'DISBURSEMENT_DATE_COLUMN',
    'TRUE_PAYMENT_DATE_COLUMN',
    'DISBURSEMENT_AMOUNT_COLUMN',
    'DATA_LOADER_NOT_AVAILABLE_MSG',
    'ABACO_SCHEMA_FILENAME'
]
