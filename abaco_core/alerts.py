"""
ABACO Alert Engine - EWMA, CUSUM, MAD-z Detection with Slack Integration
"""
from typing import List, Dict, Optional
import logging
import os
import json
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class Alert:
    """Represents a single alert."""
    
    def __init__(
        self,
        severity: str,
        category: str,
        title: str,
        message: str,
        value: Optional[float] = None,
        threshold: Optional[float] = None,
    ):
        """
        Create an alert.
        
        Args:
            severity: "critical", "warning", or "info"
            category: Alert category (e.g., "concentration", "risk", "yield")
            title: Short alert title
            message: Detailed alert message
            value: Current value that triggered alert
            threshold: Threshold that was exceeded
        """
        self.severity = severity
        self.category = category
        self.title = title
        self.message = message
        self.value = value
        self.threshold = threshold
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
        }
    
    def to_slack_block(self) -> Dict:
        """Convert alert to Slack Block Kit format."""
        emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(self.severity, "•")
        
        text = f"{emoji} *{self.title}*\n{self.message}"
        if self.value is not None and self.threshold is not None:
            text += f"\nValue: {self.value:.2f} | Threshold: {self.threshold:.2f}"
        
        color = {"critical": "#d9534f", "warning": "#f0ad4e", "info": "#5bc0de"}.get(self.severity, "#999999")
        
        return {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        }


class AlertEngine:
    """
    Alert engine with statistical detection methods.
    """
    
    def __init__(
        self,
        ewma_alpha: float = 0.3,
        cusum_threshold: float = 5.0,
        mad_z_threshold: float = 3.0,
    ):
        """
        Initialize alert engine.
        
        Args:
            ewma_alpha: EWMA smoothing factor (0 < alpha <= 1)
            cusum_threshold: CUSUM threshold for detecting shifts
            mad_z_threshold: MAD-based z-score threshold
        """
        self.ewma_alpha = ewma_alpha
        self.cusum_threshold = cusum_threshold
        self.mad_z_threshold = mad_z_threshold
    
    def _ewma(self, series: pd.Series) -> pd.Series:
        """Calculate Exponentially Weighted Moving Average."""
        return series.ewm(alpha=self.ewma_alpha, adjust=False).mean()
    
    def _cusum(self, series: pd.Series, target: float = 0.0) -> pd.Series:
        """Calculate CUSUM (Cumulative Sum) for detecting shifts."""
        deviations = series - target
        cusum = deviations.cumsum()
        return cusum
    
    def _mad_z_score(self, value: float, series: pd.Series) -> float:
        """Calculate MAD-based z-score (robust to outliers)."""
        median = series.median()
        mad = np.median(np.abs(series - median))
        if mad == 0:
            return 0.0
        return (value - median) / (1.4826 * mad)
    
    def concentration_alerts(
        self,
        exposures_by_client: pd.Series,
        exposures_mom: Optional[pd.Series] = None,
        top_n: int = 5,
        top_1_threshold: float = 0.15,
        top_5_threshold: float = 0.40,
    ) -> List[Alert]:
        """
        Generate concentration alerts.
        
        Args:
            exposures_by_client: Series indexed by customer_id with exposure amounts
            exposures_mom: Optional Series of month-over-month changes in bps
            top_n: Number of top clients to monitor
            top_1_threshold: Maximum share for top client (default 15%)
            top_5_threshold: Maximum share for top 5 clients (default 40%)
        
        Returns:
            List of Alert objects
        """
        alerts = []
        
        if len(exposures_by_client) == 0:
            return alerts
        
        total = exposures_by_client.sum()
        if total == 0:
            return alerts
        
        top_clients = exposures_by_client.nlargest(top_n)
        
        # Top 1 client concentration
        top_1_share = top_clients.iloc[0] / total
        if top_1_share > top_1_threshold:
            alerts.append(Alert(
                severity="critical" if top_1_share > top_1_threshold * 1.2 else "warning",
                category="concentration",
                title="Top Client Concentration",
                message=f"Top client represents {top_1_share*100:.1f}% of portfolio",
                value=top_1_share * 100,
                threshold=top_1_threshold * 100,
            ))
        
        # Top 5 concentration
        if len(top_clients) >= 5:
            top_5_share = top_clients.iloc[:5].sum() / total
            if top_5_share > top_5_threshold:
                alerts.append(Alert(
                    severity="warning",
                    category="concentration",
                    title="Top 5 Client Concentration",
                    message=f"Top 5 clients represent {top_5_share*100:.1f}% of portfolio",
                    value=top_5_share * 100,
                    threshold=top_5_threshold * 100,
                ))
        
        # Month-over-month concentration changes
        if exposures_mom is not None and len(exposures_mom) > 0:
            for client_id in top_clients.index:
                if client_id in exposures_mom.index:
                    mom_change_bps = exposures_mom[client_id]
                    if abs(mom_change_bps) > 200:  # 200 bps threshold
                        alerts.append(Alert(
                            severity="info",
                            category="concentration",
                            title=f"Concentration Shift - Client {client_id}",
                            message=f"Month-over-month change: {mom_change_bps:+.0f} bps",
                            value=mom_change_bps,
                            threshold=200.0,
                        ))
        
        return alerts
    
    def risk_alerts(
        self,
        npl180_mom_bps: float,
        rollrates_hist: Optional[pd.DataFrame] = None,
        dpd_7d_growth: Optional[float] = None,
        npl180_threshold_bps: float = 50.0,
        dpd_growth_threshold: float = 1.5,
    ) -> List[Alert]:
        """
        Generate risk alerts.
        
        Args:
            npl180_mom_bps: NPL 180+ month-over-month change in basis points
            rollrates_hist: Historical roll rates DataFrame
            dpd_7d_growth: 7-day DPD growth ratio
            npl180_threshold_bps: Threshold for NPL 180+ MoM change
            dpd_growth_threshold: Threshold for DPD growth ratio
        
        Returns:
            List of Alert objects
        """
        alerts = []
        
        # NPL 180+ month-over-month
        if abs(npl180_mom_bps) > npl180_threshold_bps:
            alerts.append(Alert(
                severity="critical" if npl180_mom_bps > npl180_threshold_bps * 2 else "warning",
                category="risk",
                title="NPL 180+ Spike",
                message=f"NPL 180+ increased by {npl180_mom_bps:.0f} bps month-over-month",
                value=npl180_mom_bps,
                threshold=npl180_threshold_bps,
            ))
        
        # Roll rate CUSUM detection
        if rollrates_hist is not None and len(rollrates_hist) > 10:
            if "30_60" in rollrates_hist.columns:
                cusum = self._cusum(rollrates_hist["30_60"])
                if abs(cusum.iloc[-1]) > self.cusum_threshold:
                    alerts.append(Alert(
                        severity="warning",
                        category="risk",
                        title="Roll Rate Shift Detected",
                        message=f"30-60 DPD roll rate shows sustained shift (CUSUM: {cusum.iloc[-1]:.2f})",
                        value=cusum.iloc[-1],
                        threshold=self.cusum_threshold,
                    ))
        
        # 7-day DPD growth
        if dpd_7d_growth is not None and dpd_7d_growth > dpd_growth_threshold:
            alerts.append(Alert(
                severity="critical" if dpd_7d_growth > dpd_growth_threshold * 1.5 else "warning",
                category="risk",
                title="DPD Growth Spike",
                message=f"7-day DPD growth ratio: {dpd_7d_growth:.2f}x",
                value=dpd_7d_growth,
                threshold=dpd_growth_threshold,
            ))
        
        return alerts
    
    def yield_alerts(
        self,
        apr_mix: pd.Series,
        apr_effective: Optional[pd.Series] = None,
        target_apr_mix: Optional[Dict[str, float]] = None,
        deviation_threshold: float = 5.0,
    ) -> List[Alert]:
        """
        Generate yield alerts.
        
        Args:
            apr_mix: Current APR mix (percentage by bucket)
            apr_effective: Optional historical effective APR series
            target_apr_mix: Target APR mix
            deviation_threshold: Percentage point deviation threshold
        
        Returns:
            List of Alert objects
        """
        alerts = []
        
        # APR mix vs target
        if target_apr_mix is not None:
            for bucket, target_pct in target_apr_mix.items():
                if bucket in apr_mix.index:
                    current_pct = apr_mix[bucket]
                    deviation = abs(current_pct - target_pct)
                    
                    if deviation > deviation_threshold:
                        alerts.append(Alert(
                            severity="warning",
                            category="yield",
                            title=f"APR Mix Deviation - {bucket}",
                            message=f"Current: {current_pct:.1f}%, Target: {target_pct:.1f}%",
                            value=current_pct,
                            threshold=target_pct,
                        ))
        
        # Effective APR trend
        if apr_effective is not None and len(apr_effective) > 30:
            ewma = self._ewma(apr_effective)
            latest = apr_effective.iloc[-1]
            expected = ewma.iloc[-2] if len(ewma) > 1 else ewma.iloc[-1]
            
            z_score = self._mad_z_score(latest, apr_effective)
            
            if abs(z_score) > self.mad_z_threshold:
                alerts.append(Alert(
                    severity="warning",
                    category="yield",
                    title="Effective APR Anomaly",
                    message=f"Effective APR deviation detected (MAD z-score: {z_score:.2f})",
                    value=latest,
                    threshold=expected,
                ))
        
        return alerts
    
    def liquidity_alerts(
        self,
        collections_vs_plan: float,
        bank_shortfall: bool,
        collections_threshold: float = 0.90,
    ) -> List[Alert]:
        """
        Generate liquidity alerts.
        
        Args:
            collections_vs_plan: Collections vs plan ratio (1.0 = 100%)
            bank_shortfall: Flag indicating bank balance shortfall
            collections_threshold: Minimum acceptable collections ratio
        
        Returns:
            List of Alert objects
        """
        alerts = []
        
        # Collections vs plan
        if collections_vs_plan < collections_threshold:
            alerts.append(Alert(
                severity="critical" if collections_vs_plan < collections_threshold * 0.8 else "warning",
                category="liquidity",
                title="Collections Below Plan",
                message=f"Collections at {collections_vs_plan*100:.1f}% of plan",
                value=collections_vs_plan * 100,
                threshold=collections_threshold * 100,
            ))
        
        # Bank shortfall
        if bank_shortfall:
            alerts.append(Alert(
                severity="critical",
                category="liquidity",
                title="Bank Balance Shortfall",
                message="Morning bank balance insufficient for planned disbursements",
            ))
        
        return alerts
    
    def growth_alerts(
        self,
        ltv_over_3_cac: bool,
        payback_months: Optional[float] = None,
        payback_threshold: float = 18.0,
    ) -> List[Alert]:
        """
        Generate growth alerts.
        
        Args:
            ltv_over_3_cac: Flag indicating if LTV > 3*CAC
            payback_months: Customer payback period in months
            payback_threshold: Maximum acceptable payback months
        
        Returns:
            List of Alert objects
        """
        alerts = []
        
        # LTV/CAC ratio
        if not ltv_over_3_cac:
            alerts.append(Alert(
                severity="warning",
                category="growth",
                title="LTV/CAC Below Target",
                message="Lifetime value is less than 3x customer acquisition cost",
            ))
        
        # Payback period
        if payback_months is not None and payback_months > payback_threshold:
            alerts.append(Alert(
                severity="warning",
                category="growth",
                title="Extended Payback Period",
                message=f"Customer payback period: {payback_months:.1f} months",
                value=payback_months,
                threshold=payback_threshold,
            ))
        
        return alerts
    
    def post_to_slack(self, alerts: List[Alert], webhook_url: Optional[str] = None) -> bool:
        """
        Post alerts to Slack using webhook.
        
        Args:
            alerts: List of Alert objects
            webhook_url: Slack webhook URL (or use SLACK_WEBHOOK_URL env var)
        
        Returns:
            True if posted successfully
        """
        if not alerts:
            logger.info("No alerts to post")
            return True
        
        webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
        if not webhook_url:
            logger.warning("No Slack webhook URL configured")
            return False
        
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed. Install with: pip install requests")
            return False
        
        # Group alerts by severity
        critical = [a for a in alerts if a.severity == "critical"]
        warning = [a for a in alerts if a.severity == "warning"]
        info = [a for a in alerts if a.severity == "info"]
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"ABACO Alerts ({len(alerts)} total)",
                }
            },
            {"type": "divider"},
        ]
        
        # Add critical alerts
        if critical:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Critical ({len(critical)})*"},
            })
            for alert in critical:
                blocks.append(alert.to_slack_block())
        
        # Add warnings
        if warning:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Warnings ({len(warning)})*"},
            })
            for alert in warning:
                blocks.append(alert.to_slack_block())
        
        # Add info (limit to 5)
        if info:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Info ({len(info)})*"},
            })
            for alert in info[:5]:
                blocks.append(alert.to_slack_block())
        
        payload = {"blocks": blocks}
        
        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Posted {len(alerts)} alerts to Slack")
            return True
        except Exception as e:
            logger.error(f"Failed to post to Slack: {e}")
            return False
