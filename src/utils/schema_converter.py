"""
Schema conversion utilities for Commercial-View data processing.
"""

import json
from typing import Dict, Any, Optional, Union
import pandas as pd

class SchemaConverter:
    """Convert between different schema formats for Commercial-View"""
    
    def __init__(self):
        self.type_mapping = {
            'int64': 'integer',
            'float64': 'number',
            'object': 'string',
            'bool': 'boolean',
            'datetime64[ns]': 'string'
        }
    
    def convert_pandas_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Convert pandas DataFrame schema to JSON schema format.
        
        Args:
            df: Input DataFrame
            
        Returns:
            JSON schema dictionary
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for column, dtype in df.dtypes.items():
            dtype_str = str(dtype)
            json_type = self.type_mapping.get(dtype_str, 'string')
            
            schema["properties"][column] = {
                "type": json_type,
                "description": f"Column {column} with type {dtype_str}"
            }
            
            # Add to required fields if not nullable
            if not df[column].isnull().any():
                schema["required"].append(column)
        
        return schema
    
    def convert_schema_format(self, input_schema: Dict[str, Any], target_format: str = "jsonschema") -> Dict[str, Any]:
        """
        Convert schema between different formats.
        
        Args:
            input_schema: Input schema dictionary
            target_format: Target format ('jsonschema', 'openapi', etc.)
            
        Returns:
            Converted schema dictionary
        """
        if target_format == "jsonschema":
            return self._to_json_schema(input_schema)
        elif target_format == "openapi":
            return self._to_openapi_schema(input_schema)
        else:
            return input_schema
    
    def _to_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to JSON Schema format"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }
    
    def _to_openapi_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to OpenAPI schema format"""
        return {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }

def convert_dataframe_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convert DataFrame to schema format.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Schema dictionary
    """
    converter = SchemaConverter()
    return converter.convert_pandas_schema(df)

def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate data against schema.
    
    Args:
        data: Data to validate
        schema: Schema to validate against
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Basic validation - check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                return False
        
        # Check property types
        properties = schema.get("properties", {})
        for key, value in data.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if not _validate_type(value, expected_type):
                    return False
        
        return True
    except Exception:
        return False

def _validate_type(value: Any, expected_type: Optional[str]) -> bool:
    """Validate value type against expected type"""
    if expected_type is None:
        return True
    
    type_map = {
        'string': str,
        'integer': int,
        'number': (int, float),
        'boolean': bool,
        'array': list,
        'object': dict
    }
    
    expected_python_type = type_map.get(expected_type)
    if expected_python_type is None:
        return True
    
    return isinstance(value, expected_python_type)
        desc = name.replace('_', ' ')
        
        # Add sample values if available (limited to 2)
        if sample_values and len(sample_values) > 0:
            samples = sample_values[:2]
            samples_str = ', '.join(f'"{s}"' if isinstance(s, str) else str(s) for s in samples)
            if len(sample_values) > 2:
                samples_str += ', ...'
            desc += f". Examples: {samples_str}"
        
        return desc
    
    def generate_all_models(self, output_dir: Union[str, Path]) -> Dict[str, str]:
        """Generate models for all datasets in the schema."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py to make it a package
        with open(output_dir / "__init__.py", 'w') as f:
            f.write('"""Auto-generated data models."""\n\n')
            
            # Import all models
            for dataset_name in self.datasets:
                if self.datasets[dataset_name].get("exists", False):
                    class_name = ''.join(word.capitalize() for word in dataset_name.split())
                    f.write(f"from .{class_name.lower()} import {class_name}\n")
                    
            f.write("\n__all__ = [\n")
            for dataset_name in self.datasets:
                if self.datasets[dataset_name].get("exists", False):
                    class_name = ''.join(word.capitalize() for word in dataset_name.split())
                    f.write(f'    "{class_name}",\n')
            f.write("]\n")
        
        results = {}
        for dataset_name, dataset_info in self.datasets.items():
            if dataset_info.get("exists", False):
                model_code = self.generate_pydantic_model(dataset_name, output_dir)
                results[dataset_name] = model_code
                
        return results


def convert_schema(input_data: dict) -> dict:
    """
    Convert schema format for Commercial-View processing.
    
    Args:
        input_data: Input data dictionary
        
    Returns:
        Converted schema dictionary
    """
    # Implementation here
    return input_data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert JSON schema to Pydantic models")
    parser.add_argument("schema_file", help="Path to schema JSON file")
    parser.add_argument("--output", help="Output directory for model files")
    
    args = parser.parse_args()
    
    converter = SchemaConverter(args.schema_file)
    
    if args.output:
        results = converter.generate_all_models(args.output)
        print(f"Generated {len(results)} models in {args.output}:")
        for dataset_name in results:
            print(f"  - {dataset_name}")
    else:
        # Print all models to stdout
        for dataset_name in converter.datasets:
            if converter.datasets[dataset_name].get("exists", False):
                print(f"\n# {dataset_name} Model\n")
                print(converter.generate_pydantic_model(dataset_name))
            "array": "list"
        }
        
        return type_mapping.get(dtype.lower(), "str")
    
    def _generate_description(self, name: str, dtype: str, sample_values: List[Any]) -> str:
        """Generate a description for a field based on available information.
        
        Args:
            name: Column name
            dtype: Data type
            sample_values: Sample values from the schema
            
        Returns:
            Description string
        """
        desc = name.replace('_', ' ').capitalize()
        
        # Add type information
        if dtype:
            desc += f" ({dtype})"
        
        # Add sample values if available (limited to 2)
        if sample_values and len(sample_values) > 0:
            samples = sample_values[:2]
            samples_str = ', '.join(str(s) for s in samples)
            if len(sample_values) > 2:
                samples_str += ', ...'
            desc += f". Examples: {samples_str}"
        
        return desc


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert JSON schema to Pydantic models")
    parser.add_argument("schema_file", help="Path to schema JSON file")
    parser.add_argument("--dataset", help="Dataset name to convert", required=True)
    parser.add_argument("--class-name", help="Class name for the model")
    parser.add_argument("--output", help="Output Python file")
    
    args = parser.parse_args()
    
    converter = SchemaConverter(args.schema_file)
    code = converter.generate_pydantic_model(
        args.dataset,
        args.class_name,
        args.output
    )
    
    if not args.output:
        print(code)
