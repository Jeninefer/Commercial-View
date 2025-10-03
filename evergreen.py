import pandas as pd
def monthly_cohort(df: pd.DataFrame, customer_id: str, dt_col: str) -> pd.DataFrame:
    """
    Computes a monthly cohort retention matrix for a given customer event DataFrame.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing customer event data.
        customer_id (str): Name of the column identifying unique customers.
        dt_col (str): Name of the column containing event timestamps (must be parseable as dates).

    Returns:
        pd.DataFrame: A DataFrame where each row represents a cohort (customers grouped by their first month),
            each column represents a month, and each value is the retention rate (fraction of the cohort active in that month).
    """
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
    """
    Flags customer reactivations based on gaps between events.

    Parameters
    ----------
    events : pd.DataFrame
        DataFrame containing customer event data.
    customer_id : str
        Name of the column identifying customers.
    dt_col : str
        Name of the column containing event timestamps.
    gap_days : int, optional
        Number of days that must elapse between two events for the later event to be considered a "reactivation" (default is 90).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns [customer_id, dt_col, "reactivated"], where "reactivated" is a boolean indicating if the event is a reactivation (i.e., the gap since the previous event exceeds `gap_days`).

    Reactivation logic
    -----------------
    For each customer, events are sorted chronologically. If the gap (in days) between the current event and the previous event exceeds `gap_days`, the event is flagged as a reactivation.
    """
    d = events[[customer_id, dt_col]].copy()
    d[dt_col] = pd.to_datetime(d[dt_col])
    d = d.sort_values([customer_id, dt_col])
    d["prev"] = d.groupby(customer_id)[dt_col].shift(1)
    d["gap"] = (d[dt_col] - d["prev"]).dt.days
    d["reactivated"] = (d["gap"] > gap_days).fillna(False)
    return d[[customer_id, dt_col, "reactivated"]]
