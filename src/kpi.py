"""
KPI Calculation Module for Commercial-View

Provides functions to calculate portfolio-level and marketing KPIs
from loan and funnel data.
"""

import logging
from typing import Dict, Any, Optional, Union
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Constants
DEFAULT_DPD_THRESHOLD_30 = 30
DEFAULT_DPD_THRESHOLD_60 = 60
DEFAULT_DPD_THRESHOLD_90 = 90

# Column name mappings for flexibility
COLUMN_MAPPINGS = {
    "outstanding": ["outstanding_principal", "outstanding_balance", "outstanding"],
    "interest_rate": ["interest_rate", "rate", "apr", "Interest Rate APR"],
    "loan_amount": ["loan_amount", "disbursement_amount", "Disbursement Amount"],
    "dpd": ["dpd", "days_past_due", "Days in Default"],
    "bucket": ["delinquency_bucket", "dpd_bucket", "risk_bucket"],
}


def _get_column_safe(df: pd.DataFrame, column_aliases: list) -> Optional[pd.Series]:
    """
    Safely get a column from DataFrame using multiple possible names.

    Args:
        df: DataFrame to search
        column_aliases: List of possible column names

    Returns:
        Series if found, None otherwise
    """
    for col in column_aliases:
        if col in df.columns:
            return df[col]
    return None


def _safe_sum(series: Optional[pd.Series], default: float = 0.0) -> float:
    """Safely sum a series, handling None and NaN values."""
    if series is None:
        return default
    return float(series.sum(skipna=True))


def _safe_mean(
    series: Optional[pd.Series], default: Optional[float] = None
) -> Optional[float]:
    """Safely calculate mean of a series, handling None and NaN values."""
    if series is None:
        return default
    mean_val = series.mean(skipna=True)
    return float(mean_val) if not pd.isna(mean_val) else default


def _safe_count(condition: Optional[pd.Series], default: int = 0) -> int:
    """Safely count boolean series."""
    if condition is None:
        return default
    return int(condition.sum())


def calculate_basic_portfolio_metrics(loan_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate basic portfolio metrics.

    Args:
        loan_df: DataFrame containing loan data

    Returns:
        Dictionary with basic portfolio metrics
    """
    metrics = {}

    # Get column references
    outstanding = _get_column_safe(loan_df, COLUMN_MAPPINGS["outstanding"])
    interest_rate = _get_column_safe(loan_df, COLUMN_MAPPINGS["interest_rate"])
    loan_amount = _get_column_safe(loan_df, COLUMN_MAPPINGS["loan_amount"])

    # Calculate metrics
    metrics["total_portfolio_outstanding"] = _safe_sum(outstanding)
    metrics["number_of_loans"] = int(len(loan_df))
    metrics["average_interest_rate"] = _safe_mean(interest_rate)
    metrics["average_loan_size"] = _safe_mean(loan_amount)

    # Derived metrics
    if metrics["number_of_loans"] > 0:
        metrics["average_outstanding_per_loan"] = (
            metrics["total_portfolio_outstanding"] / metrics["number_of_loans"]
        )

    return metrics


def calculate_delinquency_metrics(
    loan_df: pd.DataFrame, dpd_threshold: int = DEFAULT_DPD_THRESHOLD_30
) -> Dict[str, Any]:
    """
    Calculate delinquency and risk metrics.

    Args:
        loan_df: DataFrame containing loan data
        dpd_threshold: Days past due threshold (default: 30)

    Returns:
        Dictionary with delinquency metrics
    """
    metrics = {}

    # Get column references
    dpd = _get_column_safe(loan_df, COLUMN_MAPPINGS["dpd"])
    outstanding = _get_column_safe(loan_df, COLUMN_MAPPINGS["outstanding"])
    bucket = _get_column_safe(loan_df, COLUMN_MAPPINGS["bucket"])

    if dpd is None:
        logger.warning("DPD column not found, skipping delinquency metrics")
        return metrics

    # Calculate delinquency counts and amounts
    delinquent_mask = dpd > dpd_threshold
    metrics[f"loans_{dpd_threshold}plus"] = _safe_count(delinquent_mask)

    if outstanding is not None:
        total_outstanding = _safe_sum(outstanding)
        delinquent_outstanding = _safe_sum(outstanding[delinquent_mask])

        metrics[f"portfolio_at_risk_{dpd_threshold}"] = delinquent_outstanding
        metrics[f"percent_portfolio_at_risk_{dpd_threshold}"] = (
            (delinquent_outstanding / total_outstanding * 100.0)
            if total_outstanding > 0
            else 0.0
        )

    # Bucket distribution
    if bucket is not None:
        try:
            bucket_counts = bucket.value_counts().to_dict()
            metrics["delinquency_distribution"] = bucket_counts
        except Exception as e:
            logger.error(f"Error calculating bucket distribution: {e}")

    return metrics


def calculate_advanced_risk_metrics(loan_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate advanced risk metrics.

    Args:
        loan_df: DataFrame containing loan data

    Returns:
        Dictionary with advanced risk metrics
    """
    metrics = {}

    # Get columns
    dpd = _get_column_safe(loan_df, COLUMN_MAPPINGS["dpd"])
    outstanding = _get_column_safe(loan_df, COLUMN_MAPPINGS["outstanding"])

    if dpd is None or outstanding is None:
        logger.warning("Required columns not found for advanced risk metrics")
        return metrics

    try:
        # NPL calculation (90+ days)
        npl_mask = dpd >= DEFAULT_DPD_THRESHOLD_90
        npl_amount = _safe_sum(outstanding[npl_mask])
        total_outstanding = _safe_sum(outstanding)

        metrics["npl_amount"] = npl_amount
        metrics["npl_ratio"] = (
            (npl_amount / total_outstanding * 100.0) if total_outstanding > 0 else 0.0
        )
        metrics["npl_count"] = _safe_count(npl_mask)

        # Vintage analysis by DPD bands
        metrics["vintage_0_30"] = _safe_count(dpd <= 30)
        metrics["vintage_31_60"] = _safe_count((dpd > 30) & (dpd <= 60))
        metrics["vintage_61_90"] = _safe_count((dpd > 60) & (dpd <= 90))
        metrics["vintage_90plus"] = _safe_count(dpd > 90)

    except Exception as e:
        logger.error(f"Error calculating advanced risk metrics: {e}")

    return metrics


def calculate_portfolio_kpis(loan_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio-level KPIs from the loan dataset.

    Args:
        loan_df: DataFrame containing loan data with columns like
                outstanding_principal, interest_rate, loan_amount, dpd, etc.

    Returns:
        Dictionary of KPI names to values including:
        - Basic portfolio metrics (outstanding, count, averages)
        - Delinquency metrics (PAR, delinquency distribution)
        - Risk metrics (NPL ratio, vintage analysis)
    """
    if loan_df is None or loan_df.empty:
        logger.warning("Loan dataframe is empty, portfolio KPIs will be empty.")
        return {}

    kpis = {}

    try:
        # Calculate different metric groups
        basic_metrics = calculate_basic_portfolio_metrics(loan_df)
        delinquency_metrics = calculate_delinquency_metrics(loan_df)
        risk_metrics = calculate_advanced_risk_metrics(loan_df)

        # Merge all metrics
        kpis.update(basic_metrics)
        kpis.update(delinquency_metrics)
        kpis.update(risk_metrics)

        # Add metadata
        kpis["calculation_timestamp"] = pd.Timestamp.now().isoformat()
        kpis["data_rows_processed"] = len(loan_df)

        logger.info(f"✅ Calculated {len(kpis)} portfolio KPIs successfully")

    except Exception as e:
        logger.error(f"Error calculating portfolio KPIs: {e}", exc_info=True)
        kpis["error"] = str(e)

    return kpis


def calculate_marketing_kpis(
    funnel_data: Optional[Union[pd.DataFrame, Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Calculate marketing funnel KPIs (leads, conversion rates, etc.).

    Args:
        funnel_data: DataFrame or dict with funnel stage counts
                    Expected keys/columns: 'leads', 'opportunities', 'loans'

    Returns:
        Dictionary with marketing KPIs including:
        - Conversion rates at each stage
        - Total counts for each stage
        - Overall funnel efficiency
    """
    if funnel_data is None:
        logger.info("No funnel data provided, skipping marketing KPIs.")
        return {}

    kpis = {}

    try:
        # Convert to dict if DataFrame
        if isinstance(funnel_data, pd.DataFrame):
            if funnel_data.empty:
                logger.warning("Funnel data is empty")
                return {}
            # Assume single row or aggregate
            fd = (
                funnel_data.iloc[0].to_dict()
                if len(funnel_data) == 1
                else funnel_data.sum().to_dict()
            )
        else:
            fd = funnel_data

        # Extract stage counts
        leads = float(fd.get("leads", 0))
        opportunities = float(fd.get("opportunities", 0))
        loans = float(fd.get("loans", 0))

        # Store counts
        kpis["total_leads"] = int(leads)
        kpis["total_opportunities"] = int(opportunities)
        kpis["total_loans_from_leads"] = int(loans)

        # Calculate conversion rates
        if leads > 0:
            kpis["lead_to_opportunity_rate"] = round((opportunities / leads) * 100.0, 2)
            kpis["lead_to_loan_rate"] = round((loans / leads) * 100.0, 2)

        if opportunities > 0:
            kpis["opportunity_to_loan_rate"] = round((loans / opportunities) * 100.0, 2)

        # Overall funnel efficiency
        if leads > 0:
            kpis["overall_conversion_rate"] = round((loans / leads) * 100.0, 2)

        # Add metadata
        kpis["calculation_timestamp"] = pd.Timestamp.now().isoformat()

        logger.info(f"✅ Calculated {len(kpis)} marketing KPIs successfully")

    except Exception as e:
        logger.error(f"Error calculating marketing KPIs: {e}", exc_info=True)
        kpis["error"] = str(e)

    return kpis


def export_kpis_to_json(kpis: Dict[str, Any], output_path: str) -> bool:
    """
    Export KPIs to JSON file.

    Args:
        kpis: Dictionary of KPIs
        output_path: Path to output JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        import json
        from pathlib import Path

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Convert any non-JSON-serializable types
        serializable_kpis = {}
        for key, value in kpis.items():
            if isinstance(value, (np.integer, np.floating)):
                serializable_kpis[key] = float(value)
            elif isinstance(value, np.ndarray):
                serializable_kpis[key] = value.tolist()
            else:
                serializable_kpis[key] = value

        # Write to file
        with open(output_path, "w") as f:
            json.dump(serializable_kpis, f, indent=2)

        logger.info(f"✅ KPIs exported to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error exporting KPIs to JSON: {e}")
        return False


def export_kpis_to_csv(kpis: Dict[str, Any], output_path: str) -> bool:
    """
    Export KPIs to CSV file.

    Args:
        kpis: Dictionary of KPIs
        output_path: Path to output CSV file

    Returns:
        True if successful, False otherwise
    """
    try:
        from pathlib import Path

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        df = pd.DataFrame([kpis])

        # Write to CSV
        df.to_csv(output_path, index=False)

        logger.info(f"✅ KPIs exported to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error exporting KPIs to CSV: {e}")
        return False
