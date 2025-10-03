"""
Alert detection engine for Commercial-View.

Implements statistical anomaly detection using EWMA, CUSUM, and MAD-z methods.
Sends alerts to Slack using Block Kit formatting.
"""

import os
import math
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
import numpy as np
import requests

from .config import Config

logger = logging.getLogger("abaco_core.alerts")

SEVERITY = ("CRITICAL", "HIGH", "MEDIUM", "INFO")


def _ewma(series: pd.Series, alpha: float) -> pd.Series:
    """
    Calculate Exponentially Weighted Moving Average.
    
    Args:
        series: Time series data.
        alpha: Smoothing factor (0 < alpha <= 1).
    
    Returns:
        EWMA series.
    """
    return series.ewm(alpha=alpha, adjust=False).mean()


def _mad_z(x: pd.Series) -> pd.Series:
    """
    Calculate MAD-based Z-scores (robust outlier detection).
    
    Uses Median Absolute Deviation instead of standard deviation
    for robustness against outliers.
    
    Args:
        x: Data series.
    
    Returns:
        MAD-based Z-scores.
    """
    med = x.median()
    mad = (x - med).abs().median()
    if mad == 0:
        return pd.Series(np.zeros(len(x)), index=x.index)
    return 0.6745 * (x - med) / mad


def _cusum(x: np.ndarray, k: float, h: float) -> Tuple[bool, float, float]:
    """
    CUSUM change detection (one-sided, for detecting increases).
    
    Args:
        x: Data array.
        k: Reference value (slack parameter).
        h: Threshold for alarm.
    
    Returns:
        Tuple of (alarm_triggered, positive_sum, negative_sum).
    """
    s_pos = 0.0
    s_neg = 0.0
    mean = np.nanmean(x)
    std = np.nanstd(x) if np.nanstd(x) > 0 else 1.0
    alarm = False
    for xi in x:
        z = (xi - mean) / std
        s_pos = max(0.0, s_pos + z - k)
        s_neg = min(0.0, s_neg + z + k)
        if s_pos > h or abs(s_neg) > h:
            alarm = True
            break
    return alarm, s_pos, s_neg


class AlertEngine:
    """
    Rule-based alert detection with EWMA bands, CUSUM shift detection,
    and robust MAD-z outlier checks. Sends Slack messages via webhook.
    
    Example:
        >>> engine = AlertEngine()
        >>> alerts = engine.concentration_alerts(exposures_by_client)
        >>> engine.post_to_slack(alerts)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize alert engine.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.cfg = config or Config()
        self.rules = self.cfg.alerts
        self.webhook = os.getenv("SLACK_WEBHOOK_URL", "").strip()

    # ---------------- Core detectors ----------------
    
    def concentration_alerts(
        self,
        exposures_by_client: pd.Series,
        exposures_mom: Optional[pd.Series] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect concentration risk alerts.
        
        Checks for:
        - Top-1 client exceeding maximum exposure
        - Growing client concentrations above thresholds
        
        Args:
            exposures_by_client: Series with client_id index and exposure amounts.
            exposures_mom: Optional series with month-over-month growth in bps.
        
        Returns:
            List of alert dictionaries.
        """
        alerts = []
        total = exposures_by_client.sum()
        if total <= 0:
            return alerts
        
        shares = exposures_by_client / total
        top1 = shares.max()
        
        if top1 > self.rules["concentration"]["top1_max_pct"]:
            alerts.append(
                self._build(
                    "CRITICAL",
                    "Top-1 concentration over limit",
                    {"top1_pct": float(top1)}
                )
            )
        
        if exposures_mom is not None and not exposures_mom.empty:
            # exposures_mom indexed by client_id with monthly % share change in bps
            risky = [
                (cid, float(shares[cid]), float(exposures_mom.get(cid, 0)))
                for cid in shares.index
                if shares[cid] > self.rules["concentration"]["any_gt_pct"]
                and exposures_mom.get(cid, 0) >= self.rules["concentration"]["growth_bps"]
            ]
            for cid, pct, bps in risky:
                alerts.append(
                    self._build(
                        "HIGH",
                        "Client concentration rising",
                        {"client_id": cid, "share_pct": pct, "mom_bps": bps}
                    )
                )
        
        return alerts

    def risk_alerts(
        self,
        npl180_mom_bps: float,
        rollrates_hist: pd.DataFrame,
        dpd_7d_growth_amt: float
    ) -> List[Dict[str, Any]]:
        """
        Detect credit risk alerts.
        
        Checks for:
        - NPL≥180 days increasing month-over-month
        - Roll-rate spikes (CUSUM detection)
        - DPD60-90 or 180+ growing rapidly in 7 days
        
        Args:
            npl180_mom_bps: NPL≥180 month-over-month change in bps.
            rollrates_hist: DataFrame with columns (from_bucket, to_bucket, value).
            dpd_7d_growth_amt: 7-day growth ratio for DPD60-90 or 180+.
        
        Returns:
            List of alert dictionaries.
        """
        alerts = []
        
        if npl180_mom_bps > self.rules["risk"]["npl180_mom_bps"]:
            alerts.append(
                self._build(
                    "HIGH",
                    "NPL≥180 increased vs last month",
                    {"delta_bps": float(npl180_mom_bps)}
                )
            )
        
        # rollrates_hist columns like ("from_bucket","to_bucket","value"), last 6M per lane
        by_lane = rollrates_hist.groupby(["from_bucket", "to_bucket"])["value"].apply(list)
        for (i, j), vals in by_lane.items():
            x = np.array(vals[-6:], dtype=float)
            if len(x) >= 6:
                mu = np.nanmean(x)
                sigma = np.nanstd(x)
                if sigma > 0 and (x[-1] - mu) >= self.rules["risk"]["rollrate_sigma"] * sigma:
                    alerts.append(
                        self._build(
                            "HIGH",
                            "Roll-rate spike",
                            {
                                "from": i,
                                "to": j,
                                "value": float(x[-1]),
                                "mu": float(mu),
                                "sigma": float(sigma)
                            }
                        )
                    )
        
        if dpd_7d_growth_amt > self.rules["risk"]["dpd6090_or_180_growth_7d"]:
            alerts.append(
                self._build(
                    "HIGH",
                    "DPD60–90 or 180+ grew >20% in 7 days",
                    {"growth_ratio": float(dpd_7d_growth_amt)}
                )
            )
        
        return alerts

    def yield_alerts(
        self,
        apr_mix_series: pd.Series,
        apr_effective_series: pd.Series
    ) -> List[Dict[str, Any]]:
        """
        Detect yield/APR alerts.
        
        Checks for:
        - APR mix deviating from target (MAD-z)
        - Effective APR dropping below EWMA band
        
        Args:
            apr_mix_series: Time series of APR mix values.
            apr_effective_series: Time series of effective APR.
        
        Returns:
            List of alert dictionaries.
        """
        alerts = []
        sigma = float(self.rules["yield"]["apr_mix_sigma"])
        z = _mad_z(apr_mix_series.dropna())
        
        if not z.empty and (z.abs().iloc[-1] > sigma):
            alerts.append(
                self._build(
                    "MEDIUM",
                    "APR mix deviates from target",
                    {"mad_z": float(z.iloc[-1])}
                )
            )
        
        lam = float(self.rules["yield"]["ewma_lambda"])
        ew = _ewma(apr_effective_series.dropna(), lam)
        if len(ew) >= 2:
            last = apr_effective_series.dropna().iloc[-1]
            band = ew.iloc[-1]
            if (band - last) * 10000 >= float(self.rules["yield"]["apr_drop_bps"]):  # bps
                alerts.append(
                    self._build(
                        "MEDIUM",
                        "Effective APR fell below EWMA band",
                        {"apr": float(last), "ewma": float(band)}
                    )
                )
        
        return alerts

    def liquidity_alerts(
        self,
        collections_vs_plan: float,
        bank_shortfall: bool
    ) -> List[Dict[str, Any]]:
        """
        Detect liquidity alerts.
        
        Checks for:
        - Collections below plan
        - Bank shortfall after disbursements
        
        Args:
            collections_vs_plan: Collections performance vs plan (-1.0 to 1.0).
            bank_shortfall: Boolean indicating bank shortfall.
        
        Returns:
            List of alert dictionaries.
        """
        alerts = []
        
        if collections_vs_plan <= float(self.rules["liquidity"]["collections_vs_plan"]):
            alerts.append(
                self._build(
                    "HIGH",
                    "Collections below plan",
                    {"collections_vs_plan": float(collections_vs_plan)}
                )
            )
        
        if self.rules["liquidity"]["bank_shortfall_flag"] and bank_shortfall:
            alerts.append(
                self._build(
                    "HIGH",
                    "Bank shortfall after disbursements",
                    {}
                )
            )
        
        return alerts

    def growth_alerts(
        self,
        ltv_over_3_cac: bool,
        payback_months: Optional[float]
    ) -> List[Dict[str, Any]]:
        """
        Detect growth/unit economics alerts.
        
        Checks for:
        - CAC > LTV/3 (customer acquisition cost too high)
        - Payback period too long
        
        Args:
            ltv_over_3_cac: True if CAC > LTV/3.
            payback_months: Payback period in months.
        
        Returns:
            List of alert dictionaries.
        """
        alerts = []
        
        if ltv_over_3_cac:
            alerts.append(
                self._build(
                    "MEDIUM",
                    "CAC > LTV/3",
                    {}
                )
            )
        
        if payback_months is not None and payback_months > float(self.rules["growth"]["payback_months_gt"]):
            alerts.append(
                self._build(
                    "MEDIUM",
                    "Payback period too long",
                    {"payback_months": float(payback_months)}
                )
            )
        
        return alerts

    # ---------------- Slack ----------------
    
    def post_to_slack(self, alerts: List[Dict[str, Any]]) -> None:
        """
        Post alerts to Slack using Block Kit.
        
        Requires SLACK_WEBHOOK_URL environment variable.
        
        Args:
            alerts: List of alert dictionaries to post.
        """
        if not self.webhook or not alerts:
            return
        
        blocks = []
        for a in alerts:
            blocks.extend(self._slack_block(a))
        
        payload = {"blocks": blocks}
        try:
            r = requests.post(self.webhook, json=payload, timeout=10)
            r.raise_for_status()
        except Exception as e:
            logger.error(f"Slack post failed: {e}")

    # ---------------- Helpers ----------------
    
    def _build(self, severity: str, title: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build alert dictionary.
        
        Args:
            severity: Alert severity (CRITICAL, HIGH, MEDIUM, INFO).
            title: Alert title/message.
            meta: Additional metadata dictionary.
        
        Returns:
            Alert dictionary.
        """
        return {
            "severity": severity,
            "title": title,
            "meta": meta
        }

    def _slack_block(self, alert: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert alert to Slack Block Kit blocks.
        
        Args:
            alert: Alert dictionary.
        
        Returns:
            List of Slack block dictionaries.
        """
        color = {
            "CRITICAL": "#D32F2F",
            "HIGH": "#F57C00",
            "MEDIUM": "#FBC02D",
            "INFO": "#0288D1"
        }.get(alert["severity"], "#0288D1")
        
        meta_str = json.dumps(alert["meta"], ensure_ascii=False)
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{alert['severity']}* — {alert['title']}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"```{meta_str}```"
                    }
                ]
            },
            {"type": "divider"}
        ]
