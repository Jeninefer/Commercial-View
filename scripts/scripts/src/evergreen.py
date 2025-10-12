"""
Evergreen analytics module extracted from PR #7
Cohort retention and customer reactivation analysis functions
"""

import pandas as pd


def monthly_cohort(df: pd.DataFrame, customer_id: str, dt_col: str) -> pd.DataFrame:
    """Perform cohort retention analysis by grouping customers based on first activity month"""
    x: pd.DataFrame = df[[customer_id, dt_col]].copy()
    x[dt_col] = pd.to_datetime(x[dt_col]).dt.to_period("M").dt.to_timestamp()
    first: pd.Series = pd.Series(x.groupby(customer_id)[dt_col].min().rename("cohort"))  # type: ignore
    x = x.merge(first, on=customer_id)
    x["month"] = x[dt_col]
    cohort_group = x.groupby(["cohort", "month"])[customer_id]  # type: ignore
    cohort_counts: pd.DataFrame = cohort_group.nunique().reset_index()  # type: ignore
    cohort_pivot: pd.DataFrame = (
        cohort_counts.pivot(index="cohort", columns="month", values=customer_id)
        .fillna(0.0)
        .astype(float)
    )
    # Retention matrix
    base = cohort_pivot.apply(lambda r: r.iloc[0] if r.iloc[0] > 0 else 1, axis=1)  # type: ignore
    retention: pd.DataFrame = cohort_pivot.div(base, axis=0).round(3)  # type: ignore
    return retention


def reactivation_flag(
    events: pd.DataFrame, customer_id: str, dt_col: str, gap_days: int = 90
) -> pd.DataFrame:
    """Identify customer reactivation events by detecting gaps in activity"""
    d = events[[customer_id, dt_col]].copy()
    d[dt_col] = pd.to_datetime(d[dt_col]).sort_values()
    d["prev"] = d.groupby(customer_id)[dt_col].shift(1)
    d["gap"] = (d[dt_col] - d["prev"]).dt.days
    d["reactivated"] = (d["gap"] > gap_days).fillna(False)  # type: ignore
    return d[[customer_id, dt_col, "reactivated"]]
