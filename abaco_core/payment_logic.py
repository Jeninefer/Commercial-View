import pandas as pd
import numpy as np
from datetime import datetime, date
import re
from typing import Optional, List, Tuple, Union
import logging

logger = logging.getLogger("abaco_core.payment_logic")

class PaymentProcessor:
    DEFAULT_DPD_THRESHOLD = 180

    ID_PATTERNS = [
        r"^loan_id$", r"^id_loan$", r"^loanid$",
        r"^idprestamo$", r"^id_prestamo$", r"^application_id$",
        r"loan.*id", r"id.*loan", r"prestamo.*id", r"id.*prestamo"
    ]
    SCHEDULE_DATE_PATTERNS = [r"^due_date$", r"fecha_vencimiento", r"scheduled_date", r"date_due", r"installment_date"]
    SCHEDULE_AMOUNT_PATTERNS = [r"^due_amount$", r"amount_due", r"scheduled_installment", r"cuota", r"monto_cuota", r"installment_amount"]
    PAYMENT_DATE_PATTERNS = [r"^payment_date$", r"fecha_pago", r"date_paid", r"paid_date", r"date"]
    PAYMENT_AMOUNT_PATTERNS = [r"^payment_amount$", r"amount_paid", r"monto_pago", r"amount"]

    def __init__(self, dpd_threshold: Optional[int] = None):
        self.dpd_threshold = dpd_threshold or self.DEFAULT_DPD_THRESHOLD

    # ---------- Field detection ----------
    def _detect_field(self, df: pd.DataFrame, patterns: List[str]) -> Optional[str]:
        cols = list(df.columns)
        # exact
        for p in patterns:
            for c in cols:
                if c == p or c.lower() == p.lower():
                    return c
        # contains
        for p in patterns:
            p_low = p.lower()
            match = [c for c in cols if p_low in c.lower()]
            if match:
                return min(match, key=len)
        # regex
        for p in patterns:
            try:
                rgx = re.compile(p, re.IGNORECASE)
                hit = [c for c in cols if rgx.search(c)]
                if hit:
                    return min(hit, key=len)
            except re.error:
                continue
        return None

    # ---------- Standardization ----------
    def standardize_dataframes(self, schedule_df: pd.DataFrame, payments_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        sched = schedule_df.copy()
        pays = payments_df.copy()

        schedule_id = self._detect_field(sched, self.ID_PATTERNS)
        payment_id = self._detect_field(pays, self.ID_PATTERNS)
        if not schedule_id or not payment_id:
            raise ValueError("Loan ID field not found in schedule or payments data")

        sched_date = self._detect_field(sched, self.SCHEDULE_DATE_PATTERNS)
        sched_amt  = self._detect_field(sched, self.SCHEDULE_AMOUNT_PATTERNS)
        pay_date   = self._detect_field(pays, self.PAYMENT_DATE_PATTERNS)
        pay_amt    = self._detect_field(pays, self.PAYMENT_AMOUNT_PATTERNS)
        if not sched_date or not sched_amt or not pay_date or not pay_amt:
            raise ValueError("Required date/amount fields not found in schedule or payments")

        sched = sched.rename(columns={schedule_id: "loan_id", sched_date: "due_date", sched_amt: "due_amount"})
        pays  = pays.rename(columns={payment_id: "loan_id", pay_date: "payment_date", pay_amt: "payment_amount"})

        sched["due_date"] = pd.to_datetime(sched["due_date"], errors="coerce").dt.date
        pays["payment_date"] = pd.to_datetime(pays["payment_date"], errors="coerce").dt.date
        sched["due_amount"] = pd.to_numeric(sched["due_amount"], errors="coerce")
        pays["payment_amount"] = pd.to_numeric(pays["payment_amount"], errors="coerce")

        sched = sched.dropna(subset=["loan_id", "due_date"])
        pays  = pays.dropna(subset=["loan_id", "payment_date"])
        sched = sched.sort_values(["loan_id", "due_date"])
        pays  = pays.sort_values(["loan_id", "payment_date"])
        return sched, pays

    # ---------- Timeline ----------
    def calculate_payment_timeline(
        self, schedule_df: pd.DataFrame, payments_df: pd.DataFrame, reference_date: Optional[Union[datetime, date]] = None
    ) -> pd.DataFrame:
        sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        if reference_date is None:
            reference_date = datetime.utcnow().date()
        elif isinstance(reference_date, datetime):
            reference_date = reference_date.date()

        sched = sched.loc[sched["due_date"] <= reference_date].copy()
        pays  = pays.loc[pays["payment_date"] <= reference_date].copy()

        s = (sched.groupby(["loan_id", "due_date"], as_index=False)
                    .agg(due_amount=("due_amount", "sum"))
                    .rename(columns={"due_date": "date"}))
        p = (pays.groupby(["loan_id", "payment_date"], as_index=False)
                   .agg(payment_amount=("payment_amount", "sum"))
                   .rename(columns={"payment_date": "date"}))

        tl = s.merge(p, on=["loan_id", "date"], how="outer").sort_values(["loan_id", "date"])
        tl["due_amount"] = pd.to_numeric(tl["due_amount"], errors="coerce").fillna(0.0)
        tl["payment_amount"] = pd.to_numeric(tl["payment_amount"], errors="coerce").fillna(0.0)
        tl["cumulative_due"]  = tl.groupby("loan_id")["due_amount"].cumsum()
        tl["cumulative_paid"] = tl.groupby("loan_id")["payment_amount"].cumsum()
        tl["cumulative_gap"]  = tl["cumulative_due"] - tl["cumulative_paid"]
        return tl

    # ---------- DPD ----------
    def calculate_dpd(
        self, schedule_df: pd.DataFrame, payments_df: pd.DataFrame, reference_date: Optional[Union[datetime, date]] = None
    ) -> pd.DataFrame:
        if reference_date is None:
            reference_date = datetime.utcnow().date()
        elif isinstance(reference_date, datetime):
            reference_date = reference_date.date()

        sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        tl = self.calculate_payment_timeline(sched, pays, reference_date)

        idx = tl.groupby("loan_id")["date"].idxmax()
        last = tl.loc[idx, ["loan_id", "date", "cumulative_gap"]].rename(columns={"date": "status_date"})
        arrears = (tl.loc[tl["cumulative_gap"] > 0, ["loan_id", "date"]]
                     .groupby("loan_id", as_index=False).min()
                     .rename(columns={"date": "first_arrears_date"}))

        out = last.merge(arrears, on="loan_id", how="left")
        fad = pd.to_datetime(out["first_arrears_date"], errors="coerce")
        ref_dt = pd.to_datetime(reference_date)
        dpd = (ref_dt - fad).dt.days
        out["days_past_due"] = np.where(fad.notna(), np.maximum(dpd, 0), 0).astype(int)

        last_pay = pays.groupby("loan_id")["payment_date"].max().reset_index().rename(columns={"payment_date": "last_payment_date"})
        last_due = sched.groupby("loan_id")["due_date"].max().reset_index().rename(columns={"due_date": "last_due_date"})
        out = (out.merge(last_pay, on="loan_id", how="left")
                  .merge(last_due, on="loan_id", how="left"))

        out["past_due_amount"] = out["cumulative_gap"].clip(lower=0).fillna(0.0)
        out["is_default"] = out["days_past_due"] >= self.dpd_threshold
        out["reference_date"] = reference_date
        return out[["loan_id", "past_due_amount", "days_past_due", "first_arrears_date",
                    "last_payment_date", "last_due_date", "is_default", "reference_date"]]

    # ---------- Buckets ----------
    def assign_dpd_buckets(self, dpd_df: pd.DataFrame) -> pd.DataFrame:
        res = dpd_df.copy()
        d = pd.to_numeric(res["days_past_due"], errors="coerce").fillna(0).astype(int)
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
        res["dpd_bucket_value"] = np.select(cond, [0,1,30,60,90,120,150,180], default=999)
        desc_map = {
            "Current":"No payment due",
            "1-29":"Early delinquency",
            "30-59":"Delinquent 30 days",
            "60-89":"Delinquent 60 days",
            "90-119":"Default 90 days",
            "120-149":"Default 120 days",
            "150-179":"Default 150 days",
            "180+":"Default 180+ days",
        }
        res["dpd_bucket_description"] = res["dpd_bucket"].map(desc_map).fillna("Unknown")
        res["default_flag"] = d >= self.dpd_threshold
        return res
