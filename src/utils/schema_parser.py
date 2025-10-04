from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any


def load_schema(json_path: str | Path) -> Dict[str, Any]:
    path = Path(json_path).expanduser().resolve()
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_datasets(schema: Dict[str, Any]) -> List[str]:
    return list(schema.get("datasets", {}).keys())


def get_dataset_columns(schema: Dict[str, Any], dataset_name: str) -> List[Dict[str, Any]]:
    return schema.get("datasets", {}).get(dataset_name, {}).get("columns", [])


if __name__ == "__main__":
    schema = load_schema("/Users/jenineferderas/Downloads/abaco_schema_autodetected.json")
    for dataset in list_datasets(schema):
        print(f"\nDataset: {dataset}")
        for column in get_dataset_columns(schema, dataset):
            name = column["name"]
            dtype = column["dtype"]
            coerced = column.get("coerced_dtype")
            print(f"  - {name} ({coerced or dtype})")
