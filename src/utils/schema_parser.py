from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ColumnMetadata:
    """Metadata for a column in a dataset."""

    name: str
    dtype: str
    non_null: int
    nulls: int
    sample_values: List[Any]
    coerced_dtype: Optional[str] = None

    def __post_init__(self):
        if self.sample_values is None:
            self.sample_values = []


@dataclass
class ValidationError:
    """Validation error information."""

    message: str
    column_name: Optional[str] = None
    severity: str = "error"


@dataclass
class ColumnInfo:
    """Enhanced column information for commercial lending data"""

    name: str
    dtype: str
    nullable: bool = True
    unique_count: Optional[int] = None
    sample_values: List[Any] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    coerced_dtype: Optional[str] = None
    business_category: Optional[str] = None

    def __post_init__(self):
        if self.sample_values is None:
            self.sample_values = []
        if self.validation_rules is None:
            self.validation_rules = {}


@dataclass
class DatasetInfo:
    """Enhanced dataset information for commercial lending"""

    name: str
    columns: List[ColumnInfo]
    row_count: Optional[int] = None
    exists: bool = True
    dataset_type: Optional[str] = None
    business_purpose: Optional[str] = None
    data_quality_score: Optional[float] = None
    last_updated: Optional[str] = None


class CommercialLendingSchemaParser:
    """Enhanced schema parser for Commercial-View commercial lending platform"""

    def __init__(self):
        # Commercial lending field patterns for business categorization
        self.business_categories = {
            "identifier": {
                "patterns": [r".*id$", r".*_id$", r"id_.*", r".*key$", r".*number$"],
                "examples": ["loan_id", "customer_id", "account_number"],
            },
            "monetary": {
                "patterns": [
                    r".*amount.*",
                    r".*balance.*",
                    r".*payment.*",
                    r".*principal.*",
                    r".*interest.*",
                    r".*fee.*",
                    r".*cost.*",
                    r".*value.*",
                ],
                "examples": ["loan_amount", "current_balance", "monthly_payment"],
            },
            "rate_percentage": {
                "patterns": [
                    r".*rate.*",
                    r".*percent.*",
                    r".*ratio.*",
                    r".*yield.*",
                    r".*apr.*",
                ],
                "examples": ["interest_rate", "default_rate", "ltv_ratio"],
            },
            "temporal": {
                "patterns": [
                    r".*date.*",
                    r".*time.*",
                    r".*created.*",
                    r".*modified.*",
                    r".*maturity.*",
                    r".*due.*",
                    r".*term.*",
                ],
                "examples": ["origination_date", "maturity_date", "last_payment_date"],
            },
            "status_classification": {
                "patterns": [
                    r".*status.*",
                    r".*state.*",
                    r".*type.*",
                    r".*category.*",
                    r".*class.*",
                    r".*grade.*",
                    r".*rating.*",
                ],
                "examples": ["loan_status", "risk_grade", "loan_type"],
            },
            "risk_metrics": {
                "patterns": [
                    r".*risk.*",
                    r".*score.*",
                    r".*probability.*",
                    r".*loss.*",
                    r".*default.*",
                    r".*delinq.*",
                    r".*dpd.*",
                ],
                "examples": ["credit_score", "pd_score", "days_past_due"],
            },
            "geographic": {
                "patterns": [
                    r".*state.*",
                    r".*country.*",
                    r".*zip.*",
                    r".*postal.*",
                    r".*region.*",
                    r".*city.*",
                    r".*address.*",
                ],
                "examples": ["state_code", "zip_code", "country"],
            },
            "industry": {
                "patterns": [
                    r".*industry.*",
                    r".*sector.*",
                    r".*naics.*",
                    r".*sic.*",
                    r".*business.*",
                ],
                "examples": ["industry_code", "naics_code", "business_type"],
            },
        }

        # Dataset type detection patterns
        self.dataset_types = {
            "loan_portfolio": ["loan", "credit", "facility", "advance"],
            "customer_data": ["customer", "borrower", "client", "counterparty"],
            "payment_history": ["payment", "transaction", "cash_flow"],
            "collateral": ["collateral", "security", "pledge", "guarantee"],
            "financial_statements": [
                "financial",
                "income",
                "balance_sheet",
                "cashflow",
            ],
            "risk_data": ["risk", "rating", "score", "grade", "assessment"],
            "regulatory": ["regulatory", "compliance", "report", "filing"],
        }


def load_schema(json_path: str | Path) -> Dict[str, Any]:
    """Enhanced schema loading with error handling and validation"""
    path = Path(json_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)

        # Validate schema structure
        if not isinstance(schema, dict):
            raise ValueError("Schema must be a dictionary")

        # Add metadata if missing
        if "metadata" not in schema:
            schema["metadata"] = {
                "loaded_at": datetime.now().isoformat(),
                "source_file": str(path),
                "parser_version": "2.0.0",
            }

        return schema

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in schema file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load schema: {e}")


def list_datasets(schema: Dict[str, Any]) -> List[str]:
    """List all available datasets with enhanced filtering"""
    datasets = schema.get("datasets", {})

    # Filter out datasets that don't exist or are marked as inactive
    active_datasets = []
    for name, info in datasets.items():
        if isinstance(info, dict):
            exists = info.get("exists", True)
            active = info.get("active", True)
            if exists and active:
                active_datasets.append(name)
        else:
            # Legacy format - assume exists
            active_datasets.append(name)

    return sorted(active_datasets)


def get_dataset_columns(
    schema: Dict[str, Any], dataset_name: str
) -> List[Dict[str, Any]]:
    """Enhanced column retrieval with validation and enrichment"""
    datasets = schema.get("datasets", {})

    if dataset_name not in datasets:
        raise ValueError(f"Dataset '{dataset_name}' not found in schema")

    dataset_info = datasets[dataset_name]
    columns = dataset_info.get("columns", [])

    # Enrich columns with additional metadata if available
    enriched_columns = []
    for col in columns:
        if isinstance(col, dict):
            enriched_col = col.copy()

            # Add business categorization
            if "business_category" not in enriched_col:
                enriched_col["business_category"] = categorize_field(
                    col.get("name", "")
                )

            # Add validation rules if missing
            if "validation_rules" not in enriched_col:
                enriched_col["validation_rules"] = generate_validation_rules(
                    enriched_col
                )

            enriched_columns.append(enriched_col)
        else:
            # Legacy format - convert to dict
            enriched_columns.append({"name": str(col), "dtype": "unknown"})

    return enriched_columns


def get_dataset_info(schema: Dict[str, Any], dataset_name: str) -> DatasetInfo:
    """Get comprehensive dataset information"""
    datasets = schema.get("datasets", {})

    if dataset_name not in datasets:
        raise ValueError(f"Dataset '{dataset_name}' not found in schema")

    dataset_data = datasets[dataset_name]
    columns_data = get_dataset_columns(schema, dataset_name)

    columns = []
    for col_data in columns_data:
        columns.append(
            ColumnInfo(
                name=col_data.get("name", ""),
                dtype=col_data.get("dtype", "unknown"),
                coerced_dtype=col_data.get("coerced_dtype"),
                nullable=col_data.get("nullable", True),
                unique_count=col_data.get("unique_count"),
                sample_values=col_data.get("sample_values", []),
                business_category=col_data.get("business_category"),
                validation_rules=col_data.get("validation_rules", {}),
            )
        )

    return DatasetInfo(
        name=dataset_name,
        columns=columns,
        row_count=dataset_data.get("row_count"),
        exists=dataset_data.get("exists", True),
        dataset_type=dataset_data.get("dataset_type"),
        business_purpose=dataset_data.get("business_purpose"),
        data_quality_score=dataset_data.get("data_quality_score"),
        last_updated=dataset_data.get("last_updated"),
    )


def categorize_field(field_name: str) -> str:
    """Categorize field based on commercial lending business patterns"""
    if not field_name:
        return "other"

    field_lower = field_name.lower()
    parser = CommercialLendingSchemaParser()

    for category, info in parser.business_categories.items():
        for pattern in info["patterns"]:
            if re.search(pattern, field_lower):
                return category

    return "other"


def detect_dataset_type(dataset_name: str, columns: List[str]) -> str:
    """Detect dataset type based on name and column patterns"""
    dataset_lower = dataset_name.lower()
    columns_lower = [col.lower() for col in columns]

    parser = CommercialLendingSchemaParser()

    # Check dataset name first
    for dataset_type, keywords in parser.dataset_types.items():
        for keyword in keywords:
            if keyword in dataset_lower:
                return dataset_type

    # Check column patterns
    for dataset_type, keywords in parser.dataset_types.items():
        matches = sum(
            1 for keyword in keywords for col in columns_lower if keyword in col
        )
        if matches >= 2:  # At least 2 matching columns
            return dataset_type

    return "general"


def generate_validation_rules(column_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate validation rules based on column information"""
    rules = {}

    dtype = column_info.get("dtype", "")
    coerced_dtype = column_info.get("coerced_dtype", "")
    field_name = column_info.get("name", "").lower()

    # Type-based rules
    if "int" in dtype or "int" in coerced_dtype:
        rules["type"] = "integer"
        if "id" in field_name:
            rules["minimum"] = 1
    elif "float" in dtype or "float" in coerced_dtype:
        rules["type"] = "number"
        if any(term in field_name for term in ["rate", "percent"]):
            rules["minimum"] = 0
            rules["maximum"] = 100
        elif "amount" in field_name or "balance" in field_name:
            rules["minimum"] = 0
    elif "datetime" in dtype or "date" in field_name:
        rules["type"] = "string"
        rules["format"] = "date-time"
    else:
        rules["type"] = "string"

        # String length rules based on field purpose
        if "id" in field_name:
            rules["minLength"] = 1
            rules["maxLength"] = 50
        elif any(term in field_name for term in ["code", "status", "type"]):
            rules["maxLength"] = 20
        elif "description" in field_name or "notes" in field_name:
            rules["maxLength"] = 1000

    # Nullable rules
    if not column_info.get("nullable", True):
        rules["required"] = True

    return rules


def validate_dataset_schema(schema: Dict[str, Any], dataset_name: str) -> List[str]:
    """Validate dataset schema for commercial lending requirements"""
    issues = []

    try:
        dataset_info = get_dataset_info(schema, dataset_name)

        # Check for required commercial lending fields
        column_names = [col.name.lower() for col in dataset_info.columns]

        # Basic requirements for loan datasets
        if "loan" in dataset_name.lower():
            required_fields = ["loan_id", "amount", "rate", "status"]
            for field in required_fields:
                if not any(field in col_name for col_name in column_names):
                    issues.append(
                        f"Missing recommended field for loan dataset: {field}"
                    )

        # Check for data quality issues
        if dataset_info.data_quality_score and dataset_info.data_quality_score < 0.8:
            issues.append(
                f"Low data quality score: {dataset_info.data_quality_score:.2f}"
            )

        # Check for columns without proper categorization
        uncategorized_columns = [
            col.name for col in dataset_info.columns if col.business_category == "other"
        ]
        if len(uncategorized_columns) > len(dataset_info.columns) * 0.5:
            issues.append("Many columns lack business categorization")

    except Exception as e:
        issues.append(f"Schema validation error: {str(e)}")

    return issues


def get_schema_summary(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive schema summary for commercial lending"""
    summary = {
        "total_datasets": len(list_datasets(schema)),
        "dataset_types": {},
        "total_columns": 0,
        "business_categories": {},
        "data_quality": {"avg_quality_score": 0, "datasets_with_quality_issues": []},
        "metadata": schema.get("metadata", {}),
        "generated_at": datetime.now().isoformat(),
    }

    datasets = list_datasets(schema)
    quality_scores = []

    for dataset_name in datasets:
        try:
            dataset_info = get_dataset_info(schema, dataset_name)

            # Count dataset types
            dataset_type = dataset_info.dataset_type or detect_dataset_type(
                dataset_name, [col.name for col in dataset_info.columns]
            )
            summary["dataset_types"][dataset_type] = (
                summary["dataset_types"].get(dataset_type, 0) + 1
            )

            # Count total columns
            summary["total_columns"] += len(dataset_info.columns)

            # Count business categories
            for col in dataset_info.columns:
                category = col.business_category or "other"
                summary["business_categories"][category] = (
                    summary["business_categories"].get(category, 0) + 1
                )

            # Track data quality
            if dataset_info.data_quality_score:
                quality_scores.append(dataset_info.data_quality_score)
                if dataset_info.data_quality_score < 0.8:
                    summary["data_quality"]["datasets_with_quality_issues"].append(
                        {"name": dataset_name, "score": dataset_info.data_quality_score}
                    )

        except Exception as e:
            print(f"Warning: Could not analyze dataset {dataset_name}: {e}")

    if quality_scores:
        summary["data_quality"]["avg_quality_score"] = sum(quality_scores) / len(
            quality_scores
        )

    return summary


def export_schema_documentation(
    schema: Dict[str, Any], output_path: str | Path
) -> None:
    """Export comprehensive schema documentation"""
    output_file = Path(output_path)

    datasets = list_datasets(schema)
    summary = get_schema_summary(schema)

    doc_lines = [
        "# Commercial-View Schema Documentation",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        f"- Total Datasets: {summary['total_datasets']}",
        f"- Total Columns: {summary['total_columns']}",
        f"- Average Data Quality Score: {summary['data_quality']['avg_quality_score']:.2f}",
        "",
        "## Dataset Types",
    ]

    for dataset_type, count in summary["dataset_types"].items():
        doc_lines.append(f"- {dataset_type}: {count} datasets")

    doc_lines.extend(
        [
            "",
            "## Business Categories",
        ]
    )

    for category, count in summary["business_categories"].items():
        doc_lines.append(f"- {category}: {count} columns")

    doc_lines.extend(["", "## Datasets", ""])

    for dataset_name in datasets:
        try:
            dataset_info = get_dataset_info(schema, dataset_name)
            doc_lines.extend(
                [
                    f"### {dataset_name}",
                    f"- Type: {dataset_info.dataset_type or 'Unknown'}",
                    f"- Columns: {len(dataset_info.columns)}",
                    f"- Rows: {dataset_info.row_count or 'Unknown'}",
                    "",
                ]
            )

            # Validation issues
            issues = validate_dataset_schema(schema, dataset_name)
            if issues:
                doc_lines.append("**Issues:**")
                for issue in issues:
                    doc_lines.append(f"- {issue}")
                doc_lines.append("")

            doc_lines.append("**Columns:**")
            for col in dataset_info.columns:
                dtype_info = col.coerced_dtype or col.dtype
                category = col.business_category or "other"
                doc_lines.append(f"- {col.name} ({dtype_info}) - {category}")

            doc_lines.append("")

        except Exception as e:
            doc_lines.append(f"Error analyzing {dataset_name}: {e}")
            doc_lines.append("")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(doc_lines))


def _parse_column_metadata(column_data: Dict[str, Any]) -> ColumnMetadata:
    """Parse column metadata from JSON schema."""
    return ColumnMetadata(
        name=column_data.get("name", ""),
        dtype=column_data.get("dtype", "string"),
        non_null=column_data.get("non_null", 0),
        nulls=column_data.get("nulls", 0),
        sample_values=column_data.get("sample_values", []),
        coerced_dtype=column_data.get("coerced_dtype"),
    )


def _determine_python_type(dtype: str, coerced_dtype: Optional[str]) -> str:
    """Determine Python type from schema dtype."""
    if coerced_dtype == "datetime":
        return "date"

    type_mapping = {
        "string": "str",
        "float": "float",
        "int": "int",
        "boolean": "bool",
    }
    return type_mapping.get(dtype, "str")


def _generate_validators(column: ColumnMetadata) -> List[str]:
    """Generate validator strings for a column."""
    validators = []

    # Add numeric validators
    if column.dtype in ["float", "int"]:
        # Most numeric fields should be non-negative
        if "fee" in column.name.lower() or "amount" in column.name.lower():
            validators.append("ge=0")

    return validators


def _build_field_string(
    name: str,
    python_type: str,
    is_optional: bool,
    validators: List[str],
    description: str = "",
) -> str:
    """Build a Pydantic field string."""
    type_str = f"Optional[{python_type}]" if is_optional else python_type
    default = "None" if is_optional else "..."

    validator_str = ", ".join(validators)
    if validator_str:
        validator_str += ", "

    desc = description or f"Field {name}"

    return f'{name}: {type_str} = Field({default}, {validator_str}description="{desc}")'


def generate_pydantic_field(
    column: ColumnMetadata,
) -> str:
    """Generate a single Pydantic field definition."""
    python_type = _determine_python_type(column.dtype, column.coerced_dtype)
    is_optional = column.nulls > 0
    validators = _generate_validators(column)

    # Build field definition
    return _build_field_string(
        name=column.name,
        python_type=python_type,
        is_optional=is_optional,
        validators=validators,
        description=f"{column.name} field",
    )


def _validate_column_types(columns: List[ColumnMetadata]) -> List[ValidationError]:
    """Validate column type definitions."""
    errors = []
    for column in columns:
        error = _validate_single_column(column)
        if error:
            errors.append(error)
    return errors


def _validate_single_column(column: ColumnMetadata) -> Optional[ValidationError]:
    """Validate a single column's type definition."""
    if not column.dtype:
        return ValidationError(
            message=f"Missing dtype for column {column.name}",
            column_name=column.name,
        )

    if column.non_null + column.nulls == 0:
        return ValidationError(
            message=f"Invalid counts for column {column.name}",
            column_name=column.name,
        )

    return None


def validate_schema_consistency(schema: Dict[str, Any]) -> List[ValidationError]:
    """Validate schema consistency - refactored version."""
    errors = []

    # Validate datasets exist
    if "datasets" not in schema:
        errors.append(ValidationError(message="Missing 'datasets' key"))
        return errors

    # Validate each dataset
    for dataset_name, dataset_data in schema["datasets"].items():
        dataset_errors = _validate_dataset(dataset_name, dataset_data)
        errors.extend(dataset_errors)

    return errors


def _validate_dataset(name: str, data: Dict[str, Any]) -> List[ValidationError]:
    """Validate a single dataset."""
    errors = []

    if "columns" not in data:
        errors.append(
            ValidationError(
                message=f"Missing 'columns' in dataset {name}",
            )
        )
        return errors

    # Convert column dicts to ColumnMetadata objects
    columns = [_parse_column_metadata(col) for col in data["columns"]]
    column_errors = _validate_column_types(columns)
    errors.extend(column_errors)

    return errors


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Commercial-View Schema Parser")
    parser.add_argument("schema_file", help="Path to schema JSON file")
    parser.add_argument("--dataset", help="Specific dataset to analyze")
    parser.add_argument(
        "--summary", action="store_true", help="Generate schema summary"
    )
    parser.add_argument("--validate", action="store_true", help="Validate schema")
    parser.add_argument("--export-docs", help="Export documentation to file")

    args = parser.parse_args()

    try:
        schema = load_schema(args.schema_file)

        if args.summary:
            summary = get_schema_summary(schema)
            print(json.dumps(summary, indent=2))
        elif args.export_docs:
            export_schema_documentation(schema, args.export_docs)
            print(f"Documentation exported to: {args.export_docs}")
        elif args.validate:
            datasets = list_datasets(schema)
            all_issues = []

            for dataset in datasets:
                issues = validate_dataset_schema(schema, dataset)
                if issues:
                    all_issues.extend([(dataset, issue) for issue in issues])

            if all_issues:
                print("Schema validation issues found:")
                for dataset, issue in all_issues:
                    print(f"  {dataset}: {issue}")
            else:
                print("✅ Schema validation passed")
        elif args.dataset:
            dataset_info = get_dataset_info(schema, args.dataset)
            print(f"\nDataset: {dataset_info.name}")
            print(f"Type: {dataset_info.dataset_type or 'Unknown'}")
            print(f"Columns: {len(dataset_info.columns)}")
            print(f"Rows: {dataset_info.row_count or 'Unknown'}")

            print("\nColumns:")
            for col in dataset_info.columns:
                dtype_info = col.coerced_dtype or col.dtype
                category = col.business_category or "other"
                print(f"  - {col.name} ({dtype_info}) - {category}")
        else:
            # Default behavior - list all datasets and columns
            for dataset in list_datasets(schema):
                print(f"\n📊 Dataset: {dataset}")
                try:
                    for column in get_dataset_columns(schema, dataset):
                        name = column["name"]
                        dtype = column["dtype"]
                        coerced = column.get("coerced_dtype")
                        category = column.get("business_category", "other")
                        print(f"  - {name} ({coerced or dtype}) [{category}]")
                except Exception as e:
                    print(f"  Error: {e}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)
