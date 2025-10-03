import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger("abaco_core.feature_engineering")

class FeatureEngineer:
    DPD_BUCKETS = {
        "CURRENT": 0,
        "EARLY_ARREARS": 29,
        "DPD_30": 30,
        "DPD_60": 60,
        "DPD_90": 90,
        "DPD_120": 120,
        "DPD_150": 150,
        "DPD_180": 180
    }
    SEGMENTS = ["A", "B", "C", "D", "E", "F"]

    def __init__(self):
        pass

    # ----------- Segmentation by exposure -----------
    def segment_customers_by_exposure(self, loan_df: pd.DataFrame, customer_id_field: str,
                                      exposure_col: str = "outstanding_balance") -> pd.DataFrame:
        df = loan_df.copy()
        if exposure_col not in df.columns:
            olb_candidates = [c for c in df.columns if any(k in c.lower() for k in ["outstanding_balance", "olb", "current_balance", "saldo", "balance"])]
            if not olb_candidates:
                raise ValueError("Exposure column not found")
            df[exposure_col] = pd.to_numeric(df[olb_candidates[0]], errors="coerce").fillna(0.0)

        exp = (df.groupby(customer_id_field, as_index=False)[exposure_col].sum()
                 .rename(columns={exposure_col: "exposure"}))

        if exp["exposure"].nunique() < len(self.SEGMENTS):
            exp["segment"] = self.SEGMENTS[-1]
            return exp[[customer_id_field, "exposure", "segment"]]

        q = pd.qcut(exp["exposure"], q=len(self.SEGMENTS), labels=False, duplicates="drop")
        exp["segment"] = q.map({i: self.SEGMENTS[i] for i in range(q.max()+1)})
        return exp[[customer_id_field, "exposure", "segment"]]

    # ----------- DPD buckets -----------
    def assign_dpd_buckets(self, dpd_df: pd.DataFrame, dpd_col: str = "days_past_due") -> pd.DataFrame:
        res = dpd_df.copy()
        if dpd_col not in res.columns:
            raise ValueError(f"{dpd_col} not in DataFrame")
        d = pd.to_numeric(res[dpd_col], errors="coerce").fillna(0).astype(int)
        cond = [
            (d == 0),
            (d.between(1, 29)),
            (d.between(30, 59)),
            (d.between(60, 89)),
            (d.between(90, 119)),
            (d.between(120, 149)),
            (d.between(150, 179)),
            (d >= 180),
        ]
        labels = ["Current","1-29","30-59","60-89","90-119","120-149","150-179","180+"]
        res["dpd_bucket"] = np.select(cond, labels, default="Unknown")
        res["is_default"] = (d >= self.DPD_BUCKETS["DPD_90"]).astype(int)
        return res

    # ----------- Customer type -----------
    def classify_customer_type(self,
                               customer_df: pd.DataFrame,
                               loan_history_df: pd.DataFrame,
                               customer_id_field: str,
                               loan_start_date_field: str,
                               reference_date: Optional[datetime] = None) -> pd.DataFrame:
        if reference_date is None:
            reference_date = datetime.utcnow().date()

        out = customer_df.copy()
        hist = loan_history_df.copy()
        hist[loan_start_date_field] = pd.to_datetime(hist[loan_start_date_field], errors="coerce").dt.date
        hist = hist.dropna(subset=[customer_id_field, loan_start_date_field]).sort_values([customer_id_field, loan_start_date_field])

        types: Dict[Any, str] = {}
        for cid, g in hist.groupby(customer_id_field):
            dates = list(g[loan_start_date_field])
            if len(dates) == 0:
                types[cid] = "New"
                continue
            if len(dates) == 1:
                types[cid] = "New"
                continue
            gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            types[cid] = "Recovered" if any(gap > 90 for gap in gaps) else "Recurrent"

        out["customer_type"] = out[customer_id_field].map(types).fillna("New")
        return out

    # ----------- Weighted stats -----------
    def calculate_weighted_stats(self, loan_df: pd.DataFrame,
                                 weight_field: str = "outstanding_balance",
                                 metrics: Optional[List[str]] = None) -> pd.DataFrame:
        metrics = metrics or ["apr", "eir", "term"]
        df = loan_df.copy()
        if weight_field not in df.columns:
            candidates = [c for c in df.columns if any(k in c.lower() for k in ["outstanding_balance","olb","current_balance","balance","saldo"])]
            if not candidates:
                raise ValueError("Weight field not found")
            weight_field = candidates[0]
        out = {}
        for m in metrics:
            col = next((c for c in df.columns if m.lower() in c.lower()), None)
            if not col:
                continue
            tmp = df[[col, weight_field]].dropna()
            if tmp.empty or tmp[weight_field].sum() == 0:
                continue
            out[f"weighted_{m}"] = float(np.average(tmp[col], weights=tmp[weight_field]))
        return pd.DataFrame([out]) if out else pd.DataFrame()

    # ----------- Line utilization -----------
    def calculate_line_utilization(self, loan_df: pd.DataFrame,
                                   credit_line_field: str = "line_amount",
                                   loan_amount_field: str = "outstanding_balance") -> pd.DataFrame:
        df = loan_df.copy()
        if credit_line_field not in df.columns:
            cands = [c for c in df.columns if any(k in c.lower() for k in ["line_amount","credit_line","line_limit","limite"])]
            if not cands:
                return df
            credit_line_field = cands[0]
        if loan_amount_field not in df.columns:
            cands = [c for c in df.columns if any(k in c.lower() for k in ["outstanding_balance","olb","current_balance","loan_amount","monto"])]
            if not cands:
                return df
            loan_amount_field = cands[0]
        df["line_utilization"] = pd.to_numeric(df[loan_amount_field], errors="coerce") / pd.to_numeric(df[credit_line_field], errors="coerce")
        df["line_utilization"] = df["line_utilization"].clip(upper=1.0)
        return df

    # ----------- Concentration (HHI) -----------
    def calculate_hhi(self, loan_df: pd.DataFrame, customer_id_field: str,
                      exposure_field: str = "outstanding_balance") -> float:
        df = loan_df.copy()
        if exposure_field not in df.columns:
            return 0.0
        exp = df.groupby(customer_id_field)[exposure_field].sum()
        total = exp.sum()
        if total == 0:
            return 0.0
        shares = exp / total
        return float((shares.pow(2)).sum() * 10000)

    # ----------- Master enrichment -----------
    def enrich_master_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        res = df.copy()
        required = ["loan_id", "customer_id", "outstanding_balance"]
        missing = [c for c in required if c not in res.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        if "days_past_due" in res.columns:
            res = self.assign_dpd_buckets(res, "days_past_due")

        res = self.calculate_line_utilization(res)

        key_metrics = ["apr", "term", "days_past_due", "outstanding_balance", "line_utilization"]
        for m in key_metrics:
            if m in res.columns:
                s = res[m].astype(float)
                std = s.std(ddof=0)
                res[f"{m}_zscore"] = (s - s.mean()) / std if std > 0 else pd.Series(0.0, index=s.index)
        return res
