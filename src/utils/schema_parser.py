"""Helpers for inspecting dataset schemas.

Run this module as a script to print the datasets and columns defined in a
schema JSON file::

    python -m src.utils.schema_parser path/to/schema.json

If no path is provided, a schema file is expected at ``data/schema.json``
relative to the repository root.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "schema.json"


def load_schema(json_path: str | Path) -> Dict[str, Any]:
    path = Path(json_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_datasets(schema: Dict[str, Any]) -> List[str]:
    return list(schema.get("datasets", {}).keys())


def get_dataset_columns(schema: Dict[str, Any], dataset_name: str) -> List[Dict[str, Any]]:
    return schema.get("datasets", {}).get(dataset_name, {}).get("columns", [])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display datasets and columns from a schema JSON file.",
    )
    parser.add_argument(
        "schema_path",
        nargs="?",
        default=DEFAULT_SCHEMA_PATH,
        help=(
            "Path to the schema JSON file. Defaults to data/schema.json relative "
            "to the repository root."
        ),
    )
    args = parser.parse_args()

    try:
        schema = load_schema(args.schema_path)
    except FileNotFoundError as error:
        hint = (
            "Provide a valid schema path, e.g. `python -m src.utils.schema_parser "
            "/path/to/schema.json`."
        )
        raise SystemExit(f"{error}\n{hint}") from error

    for dataset in list_datasets(schema):
        print(f"\nDataset: {dataset}")
        for column in get_dataset_columns(schema, dataset):
            name = column["name"]
            dtype = column["dtype"]
            coerced = column.get("coerced_dtype")
            print(f"  - {name} ({coerced or dtype})")


if __name__ == "__main__":
    main()
