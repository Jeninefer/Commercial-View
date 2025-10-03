"""Payment Analyzer - Core analytics for loan and payment data."""

from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np
from .utils import logger, registry


class PaymentAnalyzer:
    """Analyzer for payment and loan portfolio analytics."""
    
    def __init__(self, config: Optional[Dict] = None, dpd_threshold: int = 90):
        """Initialize PaymentAnalyzer.
        
        Args:
            config: Optional configuration dictionary
            dpd_threshold: Days past due threshold for default flag (default: 90)
        """
        self.config = config or {}
        self.dpd_threshold = dpd_threshold
    
    def detect_loan_ids(self, df: pd.DataFrame) -> Tuple[str, str]:
        """Detect loan ID column in DataFrame.
        
        Args:
            df: DataFrame to search for loan ID column
            
        Returns:
            Tuple of (loan_id_column_name, loan_id_column_name)
            
        Raises:
            ValueError: If loan ID column cannot be found
        """
        candidates = [c for c in df.columns if any(k in c.lower() for k in ["loan_id", "loan", "prestamo", "credito"])]
        if not candidates:
            raise ValueError("Loan ID column not found")
        return candidates[0], candidates[0]
    
    def get_dpd_buckets(self, dpd_df: pd.DataFrame) -> pd.DataFrame:
        """
        Vectorized DPD bucketing with config override and default_flag.
        Config format (optional): config['dpd_buckets'] = [(0,0,"Current"), (1,29,"1-29"), ..., (180,None,"180+")]
        """
        if "days_past_due" not in dpd_df.columns:
            raise ValueError("Column 'days_past_due' is required")

        df = dpd_df.copy()
        dpd = pd.to_numeric(df["days_past_due"], errors="coerce").fillna(0)

        cfg = self.config.get("dpd_buckets")
        if cfg:
            # Build labeled intervals
            labels = []
            out = pd.Series(index=df.index, dtype="object")
            for low, high, label in cfg:
                labels.append(label)
                if high is None:  # open-ended
                    mask = dpd >= low
                else:
                    mask = (dpd >= low) & (dpd <= high)
                out[mask] = label
            df["dpd_bucket"] = out.fillna(labels[-1]).astype(str)
        else:
            bins   = [-np.inf, 0, 29, 59, 89, 119, 149, 179, np.inf]
            labels = ["Current", "1-29", "30-59", "60-89", "90-119", "120-149", "150-179", "180+"]
            df["dpd_bucket"] = pd.cut(dpd, bins=bins, labels=labels, right=True, include_lowest=True).astype(str)

        df["default_flag"] = (dpd >= int(self.dpd_threshold)).astype(int)
        try:
            registry.record_data_metrics(df, operation="dpd_bucketing")
        except Exception:
            pass
        return df
    
    def calculate_customer_segments(self, loans_df: pd.DataFrame, exposure_col: str = "outstanding_balance") -> pd.DataFrame:
        """Calculate customer segments based on exposure.
        
        Args:
            loans_df: DataFrame with loan data
            exposure_col: Column name for exposure amount
            
        Returns:
            DataFrame with segment column added
        """
        if exposure_col not in loans_df.columns:
            logger.warning(f"{exposure_col} not found for segmentation")
            return loans_df

        result_df = loans_df.copy()
        # detect customer id
        candidates = [c for c in result_df.columns if any(k in c.lower() for k in ["customer", "client", "borrower", "cliente"])]
        if not candidates:
            logger.warning("Customer ID column not found for segmentation")
            return result_df
        customer_col = candidates[0]

        agg = result_df.groupby(customer_col, as_index=False)[exposure_col].sum().rename(columns={exposure_col: "exposure"})
        if agg["exposure"].nunique() < 6:
            agg["segment"] = "F"  # minimal info → safest bucket
        else:
            # six quantiles A..F (A highest exposure)
            q = pd.qcut(agg["exposure"], q=6, labels=list("FEDCBA"), duplicates="drop")
            # Note: labels reversed so higher exposure → closer to A
            # If duplicates dropped, fill NAs with lowest segment
            agg["segment"] = q.astype(str).fillna("F")

        result_df = result_df.merge(agg[[customer_col, "segment"]], on=customer_col, how="left")
        return result_df
    
    def determine_customer_type(self, loans_df: pd.DataFrame, dpd_df: pd.DataFrame) -> pd.DataFrame:
        """
        Determine customer type based on loan history.
        
        New: first loan for customer
        Recurring: subsequent loan with gap ≤ 90 days
        Recovered: subsequent loan with gap > 90 days (no dependency on prior default)
        
        Args:
            loans_df: DataFrame with loan data
            dpd_df: DataFrame with DPD data
            
        Returns:
            DataFrame with customer_type column added
        """
        df = loans_df.copy()
        # detect IDs and date
        loan_id_col, _ = self.detect_loan_ids(df)
        cust_col = next((c for c in df.columns if any(k in c.lower() for k in ["customer","client","borrower","cliente"])), None)
        date_col = next((c for c in df.columns if any(k in c.lower() for k in ["origination","issue","start","fecha"]) and pd.api.types.is_datetime64_any_dtype(pd.to_datetime(df[c], errors="coerce"))), None)
        if not (cust_col and date_col):
            logger.warning("Missing customer/date columns for customer type")
            return df

        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.sort_values([cust_col, date_col, loan_id_col])
        types = []

        for cust, g in df.groupby(cust_col, sort=False):
            g = g.sort_values(date_col)
            prev_date = None
            for _, row in g.iterrows():
                cur_date = row[date_col]
                if pd.isna(cur_date) or prev_date is None:
                    lbl = "New"
                else:
                    gap = (cur_date - prev_date).days
                    lbl = "Recurring" if gap <= 90 else "Recovered"
                types.append({loan_id_col: row[loan_id_col], "customer_type": lbl})
                prev_date = cur_date

        out = pd.DataFrame(types)
        return df.merge(out, on=loan_id_col, how="left")
    
    def calculate_weighted_stats(self, loans_df: pd.DataFrame, weight_col: str = "outstanding_balance") -> Dict[str, float]:
        """Calculate weighted statistics for APR, EIR, and term.
        
        Args:
            loans_df: DataFrame with loan data
            weight_col: Column to use as weights
            
        Returns:
            Dictionary with weighted statistics
        """
        if weight_col not in loans_df.columns:
            logger.warning(f"{weight_col} not found for weighted stats")
            return {}

        alias = {
            "apr": ["apr","effective_apr","annual_percentage_rate","tasa_anual"],
            "eir": ["eir","effective_interest_rate","tasa_efectiva"],
            "term": ["term","tenor_days","tenure","plazo","plazo_dias"],
        }
        res: Dict[str,float] = {}
        base = loans_df.copy()
        base[weight_col] = pd.to_numeric(base[weight_col], errors="coerce")
        base = base[(base[weight_col] > 0) & np.isfinite(base[weight_col])]
        if base.empty:
            return res

        for key, names in alias.items():
            col = next((c for c in base.columns for n in names if n in c.lower()), None)
            if not col:
                continue
            sub = base[[col, weight_col]].copy()
            sub[col] = pd.to_numeric(sub[col], errors="coerce")
            sub = sub.dropna()
            if sub.empty or sub[weight_col].sum() == 0:
                continue
            res[f"weighted_{key}"] = float(np.average(sub[col], weights=sub[weight_col]))
        return res
    
    def calculate_hhi(self, loans_df: pd.DataFrame, exposure_col: str = "outstanding_balance", group_by: Optional[str] = None) -> float:
        """Calculate Herfindahl-Hirschman Index for concentration.
        
        Args:
            loans_df: DataFrame with loan data
            exposure_col: Column name for exposure
            group_by: Column to group by (auto-detected if None)
            
        Returns:
            HHI value (0-10000 scale)
        """
        if exposure_col not in loans_df.columns:
            logger.warning(f"{exposure_col} not found for HHI")
            return float("nan")
        if not group_by:
            group_by = next((c for c in loans_df.columns if any(k in c.lower() for k in ["customer","client","borrower","cliente","payor","deudor"])), None)
        if not group_by or group_by not in loans_df.columns:
            logger.warning("Grouping column not found for HHI")
            return float("nan")

        df = loans_df[[group_by, exposure_col]].copy()
        df[exposure_col] = pd.to_numeric(df[exposure_col], errors="coerce").fillna(0)
        total = df[exposure_col].sum()
        if total <= 0:
            return 0.0
        shares = df.groupby(group_by, as_index=False)[exposure_col].sum()[exposure_col] / total
        return float((shares.pow(2)).sum() * 10000.0)


def calculate_revenue_metrics(loans_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate revenue metrics for loans.
    
    Args:
        loans_df: DataFrame with loan data
        
    Returns:
        DataFrame with revenue metrics added
    """
    df = loans_df.copy()
    # detect columns
    pcol = next((c for c in df.columns if any(k in c.lower() for k in ["principal","loan_amount","monto_prestamo"])), None)
    rcol = next((c for c in df.columns if any(k in c.lower() for k in ["interest_rate","rate","tasa","apr","eir"])), None)
    tcol = next((c for c in df.columns if any(k in c.lower() for k in ["term","tenure","plazo"])), None)
    if not all([pcol, rcol, tcol]):
        logger.warning("Missing principal/rate/term for revenue metrics")
        return df

    df[pcol] = pd.to_numeric(df[pcol], errors="coerce")
    df[rcol] = pd.to_numeric(df[rcol], errors="coerce")
    df[tcol] = pd.to_numeric(df[tcol], errors="coerce")
    # rate in % if >1 else in decimals
    rate_decimal = np.where(df[rcol] > 1.0, df[rcol] / 100.0, df[rcol])
    term_years = df[tcol] / 12.0
    df["expected_revenue"] = (df[pcol] * rate_decimal * term_years).fillna(0)

    payout_col = next((c for c in df.columns if any(k in c.lower() for k in ["total_paid","payments_total","cash_received"])), None)
    if payout_col:
        df[payout_col] = pd.to_numeric(df[payout_col], errors="coerce").fillna(0)
        df["effective_revenue"] = (df[payout_col] - df[pcol]).fillna(0)
        df["revenue_efficiency"] = np.where(df["expected_revenue"] > 0, df["effective_revenue"] / df["expected_revenue"], np.nan)
    try:
        registry.record_data_metrics(df, operation="revenue_metrics")
    except Exception:
        pass
    return df


def calculate_line_utilization(loans_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate credit line utilization.
    
    Args:
        loans_df: DataFrame with loan data
        
    Returns:
        DataFrame with line_utilization column added
    """
    df = loans_df.copy()
    line_col = next((c for c in df.columns if any(k in c.lower() for k in ["credit_line","linea_credito","line_amount","monto_linea","limit"])), None)
    used_col = next((c for c in df.columns if any(k in c.lower() for k in ["outstanding","balance","used","saldo"])), None)
    if not (line_col and used_col):
        logger.warning("Missing columns for line utilization")
        return df
    num = pd.to_numeric(df[used_col], errors="coerce")
    den = pd.to_numeric(df[line_col], errors="coerce")
    util = np.where(den > 0, num / den, np.nan)
    df["line_utilization"] = np.clip(util, 0, 1)
    return df


def calculate_customer_dpd_stats(loans_df: pd.DataFrame, dpd_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate customer-level DPD statistics.
    
    Args:
        loans_df: DataFrame with loan data
        dpd_df: DataFrame with DPD data
        
    Returns:
        DataFrame with customer DPD statistics added
    """
    df = loans_df.copy()
    cust_col = next((c for c in df.columns if any(k in c.lower() for k in ["customer","client","borrower","cliente"])), None)
    if not cust_col:
        logger.warning("Customer column not found for DPD stats")
        return df

    analyzer = PaymentAnalyzer()
    try:
        loan_id_loans, _ = analyzer.detect_loan_ids(df)
        loan_id_dpd, _   = analyzer.detect_loan_ids(dpd_df)
    except ValueError:
        logger.warning("Loan ID columns not detected in one or both DataFrames")
        return df

    merged = df[[loan_id_loans, cust_col]].merge(
        dpd_df[[loan_id_dpd, "days_past_due"]].rename(columns={loan_id_dpd: loan_id_loans}),
        on=loan_id_loans,
        how="left"
    )
    stats = (merged
             .dropna(subset=["days_past_due"])
             .groupby(cust_col)["days_past_due"]
             .agg(dpd_mean="mean", dpd_median="median", dpd_max="max", dpd_min="min")
             .reset_index())
    return df.merge(stats, on=cust_col, how="left")
