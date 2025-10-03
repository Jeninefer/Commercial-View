import pandas as pd
def monthly_cohort(df: pd.DataFrame, customer_id: str, dt_col: str) -> pd.DataFrame:
    x = df[[customer_id, dt_col]].copy()
    x[dt_col] = pd.to_datetime(x[dt_col]).dt.to_period("M").dt.to_timestamp()
    first = x.groupby(customer_id)[dt_col].min().rename("cohort")
    x = x.merge(first, on=customer_id)
    x["month"] = x[dt_col]
    cohort_pivot = (x.groupby(["cohort","month"])[customer_id]
                      .nunique().reset_index()
                      .pivot(index="cohort", columns="month", values=customer_id)
                      .fillna(0))
    # Retention matrix
    base = cohort_pivot.apply(lambda r: r.iloc[0] if r.iloc[0] > 0 else 1, axis=1)
    retention = cohort_pivot.div(base, axis=0).round(3)
    return retention

def reactivation_flag(events: pd.DataFrame, customer_id: str, dt_col: str, gap_days: int = 90) -> pd.DataFrame:
    d = events[[customer_id, dt_col]].copy()
    d[dt_col] = pd.to_datetime(d[dt_col]).sort_values()
    d["prev"] = d.groupby(customer_id)[dt_col].shift(1)
    d["gap"] = (d[dt_col] - d["prev"]).dt.days
    d["reactivated"] = (d["gap"] > gap_days).fillna(False)
    return d[[customer_id, dt_col, "reactivated"]]
