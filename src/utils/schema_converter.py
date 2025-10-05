"""
Schema converter utility for Commercial View.

This script converts the JSON schema definition into Pydantic models,
making it easy to validate incoming data against the expected schema.

Usage:
    python schema_converter.py /path/to/schema.json --output models/
"""

import json
import os
import sys
from pathlib import Path
import re
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime


class SchemaConverter:
    """Utility for converting JSON schema to Pydantic models."""
    
    def __init__(self, schema_path: Union[str, Path]):
        """Initialize with path to schema JSON file."""
        self.schema_path = Path(schema_path)
        with open(self.schema_path, 'r') as f:
            self.schema = json.load(f)
        
        # Dataset definitions
        self.datasets = self.schema.get('datasets', {})
    
    def generate_pydantic_model(
        self,
        dataset_name: str,
        output_dir: Optional[Union[str, Path]] = None
    ) -> str:
        """Generate a Pydantic model from a dataset schema."""
        if dataset_name not in self.datasets:
            raise ValueError(f"Dataset '{dataset_name}' not found in schema")
            
        dataset = self.datasets[dataset_name]
        columns = dataset.get('columns', [])
        
        # Convert dataset name to CamelCase for class name
        class_name = ''.join(word.capitalize() for word in dataset_name.split())
        
        # Start building the model code
        code = [
            "from pydantic import BaseModel, Field, validator",
            "from typing import Optional",
            "from datetime import date, datetime\n",
            f"class {class_name}(BaseModel):",
            f'    """Schema for validating {dataset_name} records."""\n'
        ]
        
        # Process each column
        for column in columns:
            name = column.get('name', '')
            dtype = column.get('dtype', 'string')
            nulls = column.get('nulls', 0)
            non_null = column.get('non_null', 0)
            sample_values = column.get('sample_values', [])
            
            # Skip empty columns
            if not name:
                continue
                
            # Convert column name to valid Python identifier (remove spaces)
            field_name = self._to_field_name(name)
            
            # Determine Python type from schema dtype
            python_type = self._get_python_type(dtype, column.get('coerced_dtype'))
            
            # Add Optional wrapper if nulls exist
            if nulls > 0:
                type_str = f"Optional[{python_type}]"
                default = "None"
            else:
                type_str = python_type
                default = "..."
            
            # Create Field with description and validators
            desc = self._generate_description(name, sample_values)
            
            validators = []
            if python_type == "float" and "amount" in name.lower():
                validators.append("ge=0")  # Assume monetary amounts should be non-negative
            
            if validators:
                validator_str = ", ".join(validators) + ", "
            else:
                validator_str = ""
            
            field_line = f'    {field_name}: {type_str} = Field({default}, {validator_str}description="{desc}")'
            code.append(field_line)
        
        # Add Config class
        code.extend([
            "",
            "    class Config:",
            "        extra = \"ignore\"",  # Ignore extra fields when parsing
            "        anystr_strip_whitespace = True"  # Strip whitespace from strings
        ])
        
        # Convert to string
        model_code = "\n".join(code)
        
        # Optionally write to file
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{class_name.lower()}.py"
            with open(output_file, 'w') as f:
                f.write(model_code)
            
        return model_code
    
    def _to_field_name(self, column_name: str) -> str:
        """Convert column name to valid Python identifier."""
        # Replace spaces with nothing for camelCase
        parts = column_name.split()
        if not parts:
            return "field"
            
        # CamelCase conversion (first word lowercase, rest capitalized)
        field_name = parts[0].lower()
        field_name += ''.join(word.capitalize() for word in parts[1:])
        
        return field_name
    
    def _get_python_type(self, dtype: str, coerced_dtype: Optional[str] = None) -> str:
        """Get appropriate Python type for schema data type."""
        if coerced_dtype == "datetime":
            return "date"  # Use date for datetime fields
        
        type_mapping = {
            "string": "str",
            "float": "float",
            "int": "int",
            "boolean": "bool",
            "object": "dict",
            "array": "list"
        }
        
        return type_mapping.get(dtype.lower(), "str")
    
    def _generate_description(self, name: str, sample_values: List[Any]) -> str:
        """Generate field description with examples."""
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
            
        Returns:
            Python type as a string
        """
        # Use coerced type if available
        if coerced_dtype == "datetime":
            return "date"
        
        type_mapping = {
            "string": "str",
            "float": "float",
            "int": "int",
            "boolean": "bool",
            "object": "dict",
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
