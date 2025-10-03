from typing import Dict, Any, Optional, Tuple, List, Union, TypedDict
import pandas as pd

DataFramesDict = Dict[str, pd.DataFrame]

class Thresholds(TypedDict, total=False):
    runway_months_min: int
    ltv_cac_ratio_min: float
    nrr_min: float
