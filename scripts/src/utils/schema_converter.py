"""
Enhanced schema conversion utilities for Commercial-View commercial lending data processing.
"""

import json
import re
from typing import Dict, Any, Optional, Union, List, Set
from pathlib import Path
from datetime import datetime
import pandas as pd


class CommercialLendingSchemaConverter:
    """Enhanced schema converter for Commercial-View commercial lending platform"""

    def __init__(self, schema_file: Optional[str] = None):
        self.schema_file = schema_file
        self.datasets = {}

        # Enhanced type mapping for commercial lending data
        self.type_mapping = {
            "int64": "integer",
            "Int64": "integer",
            "float64": "number",
            "Float64": "number",
            "object": "string",
            "string": "string",
            "bool": "boolean",
            "boolean": "boolean",
            "datetime64[ns]": "string",
            "timedelta64[ns]": "string",
            "category": "string",
        }

        # Commercial lending specific field patterns
        self.commercial_patterns = {
            "loan_id": r".*loan.*id.*|.*id.*loan.*",
            "amount": r".*amount.*|.*balance.*|.*principal.*",
            "rate": r".*rate.*|.*interest.*|.*yield.*",
            "date": r".*date.*|.*time.*|.*created.*|.*modified.*",
            "status": r".*status.*|.*state.*|.*condition.*",
            "risk": r".*risk.*|.*score.*|.*grade.*|.*rating.*",
            "industry": r".*industry.*|.*sector.*|.*naics.*|.*sic.*",
            "geography": r".*state.*|.*country.*|.*zip.*|.*region.*",
        }

        if schema_file and Path(schema_file).exists():
            self._load_schema()

    def _load_schema(self):
        """Load schema from file"""
        try:
            with open(self.schema_file, "r") as f:
                schema_data = json.load(f)

            if isinstance(schema_data, dict) and "datasets" in schema_data:
                self.datasets = schema_data["datasets"]
            else:
                # Assume single dataset schema
                self.datasets = {"main": schema_data}

        except Exception as e:
            print(f"Warning: Could not load schema file {self.schema_file}: {e}")

    def convert_pandas_schema(
        self, df: pd.DataFrame, dataset_name: str = "dataset"
    ) -> Dict[str, Any]:
        """
        Convert pandas DataFrame schema to enhanced JSON schema format for commercial lending.

        Args:
            df: Input DataFrame
            dataset_name: Name of the dataset

        Returns:
            Enhanced JSON schema dictionary with commercial lending annotations
        """
        schema = {
            "type": "object",
            "title": f"{dataset_name.replace('_', ' ').title()} Schema",
            "description": f"Schema for {dataset_name} dataset in Commercial-View platform",
            "properties": {},
            "required": [],
            "commercial_lending": {
                "dataset_type": self._detect_dataset_type(df, dataset_name),
                "field_categories": {},
                "data_quality": self._assess_data_quality(df),
                "generated_at": datetime.now().isoformat(),
            },
        }

        for column, dtype in df.dtypes.items():
            dtype_str = str(dtype)
            json_type = self.type_mapping.get(dtype_str, "string")

            # Enhanced property definition
            property_def = {
                "type": json_type,
                "title": column.replace("_", " ").title(),
                "description": self._generate_enhanced_description(
                    column, dtype_str, df[column]
                ),
                "commercial_lending": {
                    "field_category": self._categorize_field(column),
                    "business_meaning": self._infer_business_meaning(column),
                    "data_type": dtype_str,
                    "nullable": df[column].isnull().any(),
                    "unique_count": df[column].nunique(),
                    "sample_values": self._get_sample_values(df[column]),
                },
            }

            # Add format information for specific types
            if json_type == "string" and "date" in column.lower():
                property_def["format"] = "date-time"
            elif json_type == "number" and any(
                term in column.lower() for term in ["rate", "percent"]
            ):
                property_def["format"] = "percentage"
                property_def["minimum"] = 0
                property_def["maximum"] = 100
            elif json_type == "number" and "amount" in column.lower():
                property_def["format"] = "currency"
                property_def["minimum"] = 0

            # Add constraints based on data analysis
            constraints = self._analyze_field_constraints(df[column], json_type)
            property_def.update(constraints)

            schema["properties"][column] = property_def
            schema["commercial_lending"]["field_categories"][column] = property_def[
                "commercial_lending"
            ]["field_category"]

            # Add to required fields if not nullable and has good data coverage
            null_percentage = df[column].isnull().sum() / len(df)
            if null_percentage < 0.05:  # Less than 5% null values
                schema["required"].append(column)

        return schema

    def _detect_dataset_type(self, df: pd.DataFrame, dataset_name: str) -> str:
        """Detect the type of commercial lending dataset"""
        column_names = [col.lower() for col in df.columns]

        if any("loan" in col for col in column_names):
            if any("payment" in col for col in column_names):
                return "loan_payments"
            elif any("application" in col for col in column_names):
                return "loan_applications"
            else:
                return "loan_portfolio"
        elif any("customer" in col or "borrower" in col for col in column_names):
            return "customer_data"
        elif any("collateral" in col for col in column_names):
            return "collateral_data"
        elif any("transaction" in col for col in column_names):
            return "transaction_data"
        else:
            return "general"

    def _categorize_field(self, field_name: str) -> str:
        """Categorize field based on commercial lending patterns"""
        field_lower = field_name.lower()

        for category, pattern in self.commercial_patterns.items():
            if re.search(pattern, field_lower, re.IGNORECASE):
                return category

        return "other"

    def _infer_business_meaning(self, field_name: str) -> str:
        """Infer business meaning for commercial lending fields"""
        field_lower = field_name.lower()

        business_meanings = {
            "loan_id": "Unique identifier for loan account",
            "borrower_id": "Unique identifier for borrower",
            "principal_amount": "Original loan principal amount",
            "current_balance": "Current outstanding balance",
            "interest_rate": "Annual interest rate percentage",
            "maturity_date": "Loan maturity date",
            "credit_score": "Borrower credit score",
            "industry_code": "Industry classification code",
            "collateral_value": "Estimated collateral value",
            "payment_status": "Current payment status",
            "days_past_due": "Number of days past due",
            "risk_grade": "Internal risk grade assignment",
        }

        for key, meaning in business_meanings.items():
            if key in field_lower or any(
                word in field_lower for word in key.split("_")
            ):
                return meaning

        return f"Commercial lending field: {field_name.replace('_', ' ')}"

    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality for commercial lending requirements"""
        return {
            "total_records": len(df),
            "total_fields": len(df.columns),
            "completeness_score": (
                1 - df.isnull().sum().sum() / (len(df) * len(df.columns))
            )
            * 100,
            "duplicate_rows": df.duplicated().sum(),
            "data_types_summary": df.dtypes.value_counts().to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

    def _get_sample_values(self, series: pd.Series, max_samples: int = 3) -> List[Any]:
        """Get sample values from a pandas Series"""
        try:
            # Get non-null unique values
            unique_values = series.dropna().unique()

            if len(unique_values) == 0:
                return []

            # Limit to max_samples
            samples = unique_values[:max_samples].tolist()

            # Convert numpy types to Python types for JSON serialization
            python_samples = []
            for sample in samples:
                if pd.isna(sample):
                    continue
                elif isinstance(sample, (pd.Timestamp, datetime)):
                    python_samples.append(sample.isoformat())
                elif hasattr(sample, "item"):  # numpy scalar
                    python_samples.append(sample.item())
                else:
                    python_samples.append(sample)

            return python_samples
        except Exception:
            return []

    def _analyze_field_constraints(
        self, series: pd.Series, json_type: str
    ) -> Dict[str, Any]:
        """Analyze field constraints for validation rules"""
        constraints = {}

        try:
            if json_type == "number":
                numeric_data = pd.to_numeric(series.dropna(), errors="coerce")
                if not numeric_data.empty:
                    constraints.update(
                        {
                            "minimum": float(numeric_data.min()),
                            "maximum": float(numeric_data.max()),
                            "multipleOf": None,  # Could add precision analysis
                        }
                    )

            elif json_type == "string":
                string_data = series.dropna().astype(str)
                if not string_data.empty:
                    constraints.update(
                        {
                            "minLength": int(string_data.str.len().min()),
                            "maxLength": int(string_data.str.len().max()),
                        }
                    )

                    # Check for pattern (e.g., consistent formats)
                    if (
                        string_data.nunique() < len(string_data) * 0.5
                    ):  # Less than 50% unique
                        # Could be enumerated values
                        constraints["enum"] = string_data.unique().tolist()[
                            :10
                        ]  # Limit to 10

        except Exception:
            pass  # Skip constraint analysis if it fails

        return constraints

    def _generate_enhanced_description(
        self, column: str, dtype: str, series: pd.Series
    ) -> str:
        """Generate enhanced description with commercial lending context"""
        desc = column.replace("_", " ").title()

        # Add business context
        business_meaning = self._infer_business_meaning(column)
        if business_meaning != f"Commercial lending field: {column.replace('_', ' ')}":
            desc = business_meaning

        # Add technical details
        desc += f" (Type: {dtype}"

        # Add data characteristics
        null_count = series.isnull().sum()
        total_count = len(series)
        if null_count > 0:
            desc += f", {null_count}/{total_count} null values"

        unique_count = series.nunique()
        desc += f", {unique_count} unique values)"

        return desc

    def convert_schema_format(
        self, input_schema: Dict[str, Any], target_format: str = "jsonschema"
    ) -> Dict[str, Any]:
        """Convert schema between different formats with commercial lending enhancements"""
        if target_format == "jsonschema":
            return self._to_json_schema(input_schema)
        elif target_format == "openapi":
            return self._to_openapi_schema(input_schema)
        elif target_format == "pydantic":
            return self._to_pydantic_schema(input_schema)
        else:
            return input_schema

    def _to_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to JSON Schema format"""
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f"https://commercial-view.com/schemas/{schema.get('title', 'schema').lower()}",
            "type": "object",
            "title": schema.get("title", "Commercial-View Schema"),
            "description": schema.get("description", "Commercial lending data schema"),
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
        }

        # Add commercial lending metadata
        if "commercial_lending" in schema:
            json_schema["x-commercial-lending"] = schema["commercial_lending"]

        return json_schema

    def _to_openapi_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to OpenAPI schema format"""
        openapi_schema = {
            "type": "object",
            "title": schema.get("title", "Commercial-View Schema"),
            "description": schema.get("description", "Commercial lending data schema"),
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
        }

        # Add OpenAPI-specific extensions
        if "commercial_lending" in schema:
            openapi_schema["x-commercial-lending"] = schema["commercial_lending"]

        return openapi_schema

    def _to_pydantic_schema(self, schema: Dict[str, Any]) -> str:
        """Generate Pydantic model code from schema"""
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        class_name = schema.get("title", "CommercialLendingModel").replace(" ", "")

        lines = [
            "from typing import Optional, List",
            "from datetime import datetime",
            "from pydantic import BaseModel, Field",
            "",
            f"class {class_name}(BaseModel):",
            '    """',
            f'    {schema.get("description", "Commercial lending data model")}',
            '    """',
        ]

        for prop_name, prop_def in properties.items():
            prop_type = self._get_python_type(prop_def)
            is_required = prop_name in required

            if not is_required:
                prop_type = f"Optional[{prop_type}]"

            field_def = f"Field(description='{prop_def.get('description', '')}')"
            lines.append(f"    {prop_name}: {prop_type} = {field_def}")

        return "\n".join(lines)

    def _get_python_type(self, prop_def: Dict[str, Any]) -> str:
        """Get Python type from property definition"""
        json_type = prop_def.get("type", "string")

        type_mapping = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "List",
            "object": "dict",
        }

        return type_mapping.get(json_type, "str")

    def generate_pydantic_model(
        self, dataset_name: str, output_file: Optional[str] = None
    ) -> str:
        """Generate Pydantic model for a specific dataset"""
        if dataset_name not in self.datasets:
            raise ValueError(f"Dataset {dataset_name} not found in schema")

        dataset_schema = self.datasets[dataset_name]
        model_code = self._to_pydantic_schema(dataset_schema)

        if output_file:
            with open(output_file, "w") as f:
                f.write(model_code)

        return model_code

    def generate_all_models(self, output_dir: str) -> Dict[str, str]:
        """Generate Pydantic models for all datasets"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        with open(output_path / "__init__.py", "w") as f:
            f.write('"""Commercial-View auto-generated data models."""\n\n')

            for dataset_name in self.datasets:
                if self.datasets[dataset_name].get("exists", True):
                    class_name = "".join(
                        word.capitalize() for word in dataset_name.split("_")
                    )
                    f.write(f"from .{dataset_name} import {class_name}\n")

            f.write("\n__all__ = [\n")
            for dataset_name in self.datasets:
                if self.datasets[dataset_name].get("exists", True):
                    class_name = "".join(
                        word.capitalize() for word in dataset_name.split("_")
                    )
                    f.write(f'    "{class_name}",\n')
            f.write("]\n")

        results = {}
        for dataset_name in self.datasets:
            if self.datasets[dataset_name].get("exists", True):
                output_file = output_path / f"{dataset_name}.py"
                model_code = self.generate_pydantic_model(
                    dataset_name, str(output_file)
                )
                results[dataset_name] = model_code

        return results


# Legacy compatibility
SchemaConverter = CommercialLendingSchemaConverter


def convert_dataframe_schema(
    df: pd.DataFrame, dataset_name: str = "dataset"
) -> Dict[str, Any]:
    """Convert DataFrame to enhanced schema format for commercial lending"""
    converter = CommercialLendingSchemaConverter()
    return converter.convert_pandas_schema(df, dataset_name)


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate data against schema with enhanced commercial lending rules"""
    try:
        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                return False

        # Check property types and constraints
        properties = schema.get("properties", {})
        for key, value in data.items():
            if key in properties:
                prop_def = properties[key]
                expected_type = prop_def.get("type")

                if not _validate_type(value, expected_type):
                    return False

                # Validate constraints
                if not _validate_constraints(value, prop_def):
                    return False

        return True
    except Exception:
        return False


def _validate_type(value: Any, expected_type: Optional[str]) -> bool:
    """Validate value type against expected type"""
    if expected_type is None or value is None:
        return True

    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }

    expected_python_type = type_map.get(expected_type)
    if expected_python_type is None:
        return True

    return isinstance(value, expected_python_type)


def _validate_constraints(value: Any, prop_def: Dict[str, Any]) -> bool:
    """Validate value against property constraints"""
    try:
        # Validate numeric constraints
        if isinstance(value, (int, float)):
            if "minimum" in prop_def and value < prop_def["minimum"]:
                return False
            if "maximum" in prop_def and value > prop_def["maximum"]:
                return False

        # Validate string constraints
        if isinstance(value, str):
            if "minLength" in prop_def and len(value) < prop_def["minLength"]:
                return False
            if "maxLength" in prop_def and len(value) > prop_def["maxLength"]:
                return False
            if "enum" in prop_def and value not in prop_def["enum"]:
                return False

        return True
    except Exception:
        return False


def convert_schema(input_data: dict) -> dict:
    """Convert schema format for Commercial-View processing"""
    converter = CommercialLendingSchemaConverter()
    return converter.convert_schema_format(input_data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Commercial-View Schema Converter")
    parser.add_argument("schema_file", help="Path to schema JSON file")
    parser.add_argument("--dataset", help="Dataset name to convert")
    parser.add_argument("--output", help="Output directory for model files")
    parser.add_argument(
        "--format",
        choices=["pydantic", "jsonschema", "openapi"],
        default="pydantic",
        help="Output format",
    )

    args = parser.parse_args()

    converter = CommercialLendingSchemaConverter(args.schema_file)

    if args.output:
        if args.dataset:
            # Generate single model
            model_code = converter.generate_pydantic_model(
                args.dataset, f"{args.output}/{args.dataset}.py"
            )
            print(f"Generated model for {args.dataset} in {args.output}")
        else:
            # Generate all models
            results = converter.generate_all_models(args.output)
            print(f"Generated {len(results)} models in {args.output}:")
            for dataset_name in results:
                print(f"  - {dataset_name}")
    else:
        # Print to stdout
        if args.dataset:
            if args.format == "pydantic":
                print(converter.generate_pydantic_model(args.dataset))
            else:
                schema = converter.datasets.get(args.dataset, {})
                converted = converter.convert_schema_format(schema, args.format)
                print(json.dumps(converted, indent=2))
        else:
            print("Please specify --dataset when outputting to stdout")
