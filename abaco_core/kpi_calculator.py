import pandas as pd
import numpy as np
import json
import os
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging
from .types import Thresholds

logger = logging.getLogger("abaco_core.kpi")

class KPICalculator:
    DEFAULT_EXPORT_PATH = "./abaco_runtime/exports"
    DEFAULT_THRESHOLDS: Thresholds = {
        "runway_months_min": 12,
        "ltv_cac_ratio_min": 3.0,
        "nrr_min": 1.0
    }

    def __init__(self, export_path: Optional[str] = None, thresholds: Optional[Thresholds] = None):
        self.export_path = export_path or self.DEFAULT_EXPORT_PATH
        self.thresholds: Thresholds = thresholds or self.DEFAULT_THRESHOLDS
        os.makedirs(self.export_path, exist_ok=True)

    # ---------- Safe division ----------
    def safe_division(self,
                      numerator: Union[float, pd.Series, np.ndarray],
                      denominator: Union[float, pd.Series, np.ndarray],
                      default: float = np.nan) -> Union[float, pd.Series, np.ndarray]:
        num = numerator
        den = denominator
        if np.isscalar(num) and np.isscalar(den):
            return default if den in (0, None) else num / den
        num = pd.Series(num) if not isinstance(num, (pd.Series, np.ndarray)) else num
        den = pd.Series(den) if not isinstance(den, (pd.Series, np.ndarray)) else den
        num = pd.to_numeric(num, errors="coerce")
        den = pd.to_numeric(den, errors="coerce")
        with np.errstate(divide="ignore", invalid="ignore"):
            out = num.values / den.values
        out = np.where((den.values == 0) | ~np.isfinite(out), default, out)
        return pd.Series(out, index=num.index) if isinstance(num, pd.Series) else out

    # ---------- Startup metrics ----------
    def compute_startup_metrics(self,
                                revenue_df: pd.DataFrame,
                                customer_df: pd.DataFrame,
                                expense_df: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        m: Dict[str, float] = {}
        # MRR/ARR
        if {"date","recurring_revenue"}.issubset(revenue_df.columns):
            r = revenue_df[["date","recurring_revenue"]].copy()
            r["date"] = pd.to_datetime(r["date"], errors="coerce")
            r = r.sort_values("date").dropna(subset=["date"]).tail(1)
            mrr = float(r["recurring_revenue"].iloc[0]) if not r.empty else 0.0
            m["mrr"] = mrr
            m["arr"] = mrr * 12.0
        # Churn
        if {"churn_count","start_count"}.issubset(customer_df.columns):
            m["churn_rate"] = float(self.safe_division(customer_df["churn_count"].sum(),
                                                       customer_df["start_count"].sum(), 0.0))
        elif "is_churned" in customer_df.columns:
            m["churn_rate"] = float(self.safe_division(customer_df["is_churned"].sum(), len(customer_df), 0.0))
        # NRR (ratio where 1.0 == 100%)
        if {"start_revenue","end_revenue"}.issubset(revenue_df.columns):
            m["nrr"] = float(self.safe_division(revenue_df["end_revenue"].sum(),
                                                revenue_df["start_revenue"].sum(), 0.0))
        # CAC/LTV
        if expense_df is not None and "marketing_expense" in expense_df.columns and "new_customers" in customer_df.columns:
            marketing = float(pd.to_numeric(expense_df["marketing_expense"], errors="coerce").fillna(0).sum())
            new_cust = float(pd.to_numeric(customer_df["new_customers"], errors="coerce").fillna(0).sum())
            m["cac"] = float(self.safe_division(marketing, new_cust, 0.0))
            if "revenue" in revenue_df.columns and "customer_count" in revenue_df.columns:
                arpu = float(self.safe_division(pd.to_numeric(revenue_df["revenue"], errors="coerce").sum(),
                                                pd.to_numeric(revenue_df["customer_count"], errors="coerce").sum(), 0.0))
                m["arpu"] = arpu
                if m.get("churn_rate", 0) > 0:
                    m["ltv"] = float(self.safe_division(arpu, m["churn_rate"], np.inf))
                    if m.get("cac", 0) > 0:
                        m["ltv_cac_ratio"] = float(self.safe_division(m["ltv"], m["cac"], np.nan))
        # Burn/Runway
        if expense_df is not None and {"date", "total_expense"}.issubset(expense_df.columns):
            desired_cols = ["date", "total_expense", "cash_balance"]
            cols = [col for col in desired_cols if col in expense_df.columns]
            e = expense_df[cols].copy()
            e["date"] = pd.to_datetime(e["date"], errors="coerce")
            e = e.dropna(subset=["date"]).sort_values("date")
            if len(e) >= 3:
                last3 = e.tail(3)
                monthly_burn = float(pd.to_numeric(last3["total_expense"], errors="coerce").mean())
                m["monthly_burn"] = monthly_burn
                if "cash_balance" in e.columns and not e["cash_balance"].empty:
                    cash = float(pd.to_numeric(e["cash_balance"], errors="coerce").iloc[-1])
                    m["runway_months"] = float(self.safe_division(cash, monthly_burn, np.inf)) if monthly_burn > 0 else np.inf
        return m

    # ---------- Fintech metrics ----------
    def compute_fintech_metrics(self,
                                loan_df: pd.DataFrame,
                                payment_df: Optional[pd.DataFrame] = None,
                                user_df: Optional[pd.DataFrame] = None,
                                *,
                                default_dpd_threshold: int = 180) -> Dict[str, float]:
        m: Dict[str, float] = {}
        df = loan_df.copy()

        amt_col = next((c for c in df.columns if c.lower() in {"loan_amount","amount","monto_prestamo"}), None)
        if amt_col:
            m["gmv"] = float(pd.to_numeric(df[amt_col], errors="coerce").fillna(0).sum())

        dpd_col = next((c for c in df.columns if c.lower() in {"days_past_due","dpd","dias_atraso"}), None)
        if dpd_col:
            dpd = pd.to_numeric(df[dpd_col], errors="coerce").fillna(0)
            defaults = int((dpd >= default_dpd_threshold).sum())
            base = len(df) if len(df) > 0 else np.nan
            m["default_rate"] = float(self.safe_division(defaults, base, 0.0))

        if "revenue" in df.columns and "gmv" in m and m["gmv"] > 0:
            rev = float(pd.to_numeric(df["revenue"], errors="coerce").fillna(0).sum())
            m["take_rate"] = float(self.safe_division(rev, m["gmv"], 0.0))

        apr_col = next((c for c in df.columns if "apr" in c.lower()), None)
        eir_col = next((c for c in df.columns if "eir" in c.lower()), None)
        if eir_col:
            m["avg_eir"] = float(pd.to_numeric(df[eir_col], errors="coerce").mean())
        if apr_col and eir_col:
            if "apr_eir_spread" in df.columns:
                m["avg_apr_eir_spread"] = float(pd.to_numeric(df["apr_eir_spread"], errors="coerce").mean())
            else:
                m["avg_apr_eir_spread"] = float((pd.to_numeric(df[apr_col], errors="coerce") - pd.to_numeric(df[eir_col], errors="coerce")).mean())

        if user_df is not None and "is_active" in user_df.columns:
            active = int(pd.to_numeric(user_df["is_active"], errors="coerce").fillna(0).sum())
            total = len(user_df) if len(user_df) > 0 else np.nan
            m["active_users"] = active
            m["active_rate"] = float(self.safe_division(active, total, 0.0))
        elif payment_df is not None and {"customer_id","date"}.issubset(payment_df.columns):
            tmp = payment_df.copy()
            tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
            cutoff = pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=30)
            m["active_users"] = int(tmp.loc[tmp["date"] >= cutoff, "customer_id"].nunique())

        return m

    # ---------- Valuation metrics ----------
    def compute_valuation_metrics(self, financial_df: pd.DataFrame, revenue_df: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        metrics: Dict[str, float] = {}
        try:
            if "pre_money_valuation" in financial_df.columns:
                metrics["pre_money_valuation"] = float(financial_df["pre_money_valuation"].iloc[-1])
            if "investment_amount" in financial_df.columns and "pre_money_valuation" in metrics:
                investment = float(financial_df["investment_amount"].iloc[-1])
                metrics["post_money_valuation"] = metrics["pre_money_valuation"] + investment
            if "enterprise_value" in financial_df.columns:
                metrics["enterprise_value"] = float(financial_df["enterprise_value"].iloc[-1])

            if "ebitda" in financial_df.columns and "enterprise_value" in metrics:
                ebitda = float(financial_df["ebitda"].iloc[-1])
                metrics["ev_ebitda_multiple"] = float(self.safe_division(metrics["enterprise_value"], ebitda, np.nan)) if ebitda > 0 else np.nan

            if revenue_df is not None and "revenue" in revenue_df.columns and "enterprise_value" in metrics:
                annual_revenue = float(pd.to_numeric(revenue_df["revenue"], errors="coerce").sum())
                metrics["ev_revenue_multiple"] = float(self.safe_division(metrics["enterprise_value"], annual_revenue, np.nan)) if annual_revenue > 0 else np.nan

            if {"shares_before","shares_after"}.issubset(financial_df.columns):
                before = float(financial_df["shares_before"].iloc[-1])
                after  = float(financial_df["shares_after"].iloc[-1])
                metrics["dilution"] = 1.0 - float(self.safe_division(before, after, 1.0)) if after >= before and after > 0 else 0.0
        except Exception as e:
            logger.error(f"Valuation metrics error: {e}")
        return metrics

    # ---------- Viability index ----------
    def compute_viability_index(self, startup_metrics: Dict[str, float]) -> int:
        t = self.thresholds
        runway = float(startup_metrics.get("runway_months", 0) or 0)
        ltv_cac = float(startup_metrics.get("ltv_cac_ratio", startup_metrics.get("ltv_cac", 0)) or 0)
        nrr = float(startup_metrics.get("nrr", 0) or 0)

        score = 0.0
        # Runway (40%)
        if runway >= 2*t["runway_months_min"]:
            score += 40*1.0
        elif runway >= t["runway_months_min"]:
            score += 40*0.75
        elif runway >= t["runway_months_min"]/2:
            score += 40*0.50
        elif runway > 0:
            score += 40*0.25

        # LTV/CAC (40%)
        if ltv_cac >= 2*t["ltv_cac_ratio_min"]:
            score += 40*1.0
        elif ltv_cac >= t["ltv_cac_ratio_min"]:
            score += 40*0.75
        elif ltv_cac >= t["ltv_cac_ratio_min"]/2:
            score += 40*0.50
        elif ltv_cac > 0:
            score += 40*0.25

        # NRR (20%)
        if nrr >= 1.2 * t["nrr_min"]:
            score += 20*1.0
        elif nrr >= t["nrr_min"]:
            score += 20*0.75
        elif nrr >= 0.8 * t["nrr_min"]:
            score += 20*0.50
        elif nrr > 0:
            score += 20*0.25

        return int(round(score))

    # ---------- Orchestrator ----------
    def compute_kpis(self,
                     data_dict: Dict[str, pd.DataFrame],
                     thresholds: Optional[Dict[str, float]] = None) -> Dict[str, Dict[str, float]]:
        if thresholds:
            # Only update with keys that are valid for Thresholds
            valid_thresholds = {k: v for k, v in thresholds.items() if k in self.thresholds}
            self.thresholds.update(valid_thresholds)  # partial overrides

        result: Dict[str, Dict[str, float]] = {"startup": {}, "fintech": {}, "valuation": {}, "viability": {}}

        if "revenue" in data_dict and "customer" in data_dict:
            result["startup"] = self.compute_startup_metrics(
                data_dict["revenue"], data_dict["customer"], data_dict.get("expense")
            )

        if "loan" in data_dict:
            result["fintech"] = self.compute_fintech_metrics(
                data_dict["loan"], data_dict.get("payment"), data_dict.get("user")
            )

        if "financial" in data_dict:
            result["valuation"] = self.compute_valuation_metrics(data_dict["financial"], data_dict.get("revenue"))

        if result["startup"] or result["fintech"]:
            result["viability"]["viability_index"] = self.compute_viability_index(result["startup"])
        return result

    # ---------- Export ----------
    def export_metrics_to_json(self, metrics: Dict[str, Dict[str, float]]) -> str:
        os.makedirs(self.export_path, exist_ok=True)
        payload = {"metrics": metrics, "metadata": {"timestamp": datetime.utcnow().isoformat()+"Z", "thresholds": self.thresholds}}
        path = os.path.join(self.export_path, f"startup_fintech_valuation_summary.json")
        with open(path, "w") as f:
            json.dump(payload, f, indent=2, default=str)
        return path

    def export_metrics_to_csv(self, metrics: Dict[str, Dict[str, float]]) -> Dict[str, str]:
        os.makedirs(self.export_path, exist_ok=True)
        out: Dict[str, str] = {}
        for cat, m in metrics.items():
            if not m:
                continue
            df = pd.DataFrame([m])
            path = os.path.join(self.export_path, f"{cat}_metrics.csv")
            df.to_csv(path, index=False)
            out[cat] = path
        return out

    def summarize_kpis(self, metrics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        s: Dict[str, Any] = {}
        startup = metrics.get("startup", {})
        fintech = metrics.get("fintech", {})
        valuation = metrics.get("valuation", {})
        viability = metrics.get("viability", {})

        if startup:
            s.update({k: startup.get(k) for k in ["mrr","arr","runway_months","ltv_cac_ratio","churn_rate","nrr"]})
        if fintech:
            s.update({k: fintech.get(k) for k in ["gmv","default_rate","take_rate","active_users","avg_eir"]})
        if valuation:
            s.update({k: valuation.get(k) for k in ["enterprise_value","ev_revenue_multiple","dilution"]})
        if viability:
            s["viability_index"] = viability.get("viability_index")
        return s
