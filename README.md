# Commercial-View
Principal KPI Export Tool

## Overview
A Python tool for exporting KPI (Key Performance Indicator) data to timestamped JSON files.

## Features
- Export KPI data to JSON files with automatic timestamping
- Supports nested data structures
- Automatic directory creation
- JSON formatting with indentation
- Handles non-serializable objects (like datetime) automatically
- Logging of export operations

## Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from src.kpi_exporter import KPIExporter

# Create an exporter instance
exporter = KPIExporter(export_path="exports")

# Export KPI data
kpi_data = {
    "metric": "revenue",
    "value": 150000,
    "currency": "USD"
}

filepath = exporter._export_json(kpi_data, "revenue_kpi")
print(f"Exported to: {filepath}")
```

## Example

Run the example script:
```bash
python example.py
```

This will create timestamped JSON files in the `exports/` directory.

## Running Tests

```bash
pytest tests/ -v
```

## File Structure

```
Commercial-View/
├── src/
│   ├── __init__.py
│   └── kpi_exporter.py    # Main KPI exporter implementation
├── tests/
│   ├── __init__.py
│   └── test_kpi_exporter.py    # Comprehensive test suite
├── example.py              # Example usage
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Output Format

Exported files follow the naming convention:
```
{name}_{timestamp}.json
```

Where timestamp is in ISO 8601 format: `YYYYMMDDTHHMMSSZ.json`

Example: `revenue_kpi_20231225T103045Z.json`

