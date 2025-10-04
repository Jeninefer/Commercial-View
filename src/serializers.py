from __future__ import annotations

from typing import List, Sequence, Type, TypeVar

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def _normalize_records(records: Sequence[dict]) -> List[dict]:
    normalized: List[dict] = []
    for record in records:
        normalized.append({key: (_coerce_value(value)) for key, value in record.items()})
    return normalized


def _coerce_value(value):
    if pd.isna(value):
        return None
    return value


def dataframe_to_models(df: DataFrame, model: Type[ModelT]) -> List[ModelT]:
    records = df.to_dict(orient="records")
    normalized_records = _normalize_records(records)
    instances: List[ModelT] = []
    for record in normalized_records:
        if hasattr(model, "model_validate"):
            instances.append(model.model_validate(record))  # type: ignore[attr-defined]
        else:
            instances.append(model.parse_obj(record))  # type: ignore[attr-defined]
    return instances


def dataframe_to_dicts(df: DataFrame) -> List[dict]:
    records = df.to_dict(orient="records")
    return _normalize_records(records)
