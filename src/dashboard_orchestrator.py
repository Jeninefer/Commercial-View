"""Dashboard orchestration entry point for Commercial-View."""

from __future__ import annotations

import importlib
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from dashboard_exporter import DashboardDistributionManager
from hybrid_ai import HybridAIOrchestrator

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from pipeline import CommercialViewPipeline

logger = logging.getLogger(__name__)


class DashboardOrchestrator:
    """Coordinates data pipeline, AI narratives, and distribution."""

    def __init__(
        self,
        *,
        pipeline: Optional["CommercialViewPipeline"] = None,
        ai_orchestrator: Optional[HybridAIOrchestrator] = None,
        distributor: Optional[DashboardDistributionManager] = None,
    ) -> None:
        self.pipeline = pipeline or self._create_pipeline()
        self.ai_orchestrator = ai_orchestrator or HybridAIOrchestrator()
        self.distributor = distributor or DashboardDistributionManager()

    def build_dashboard_views(self) -> Dict[str, Any]:
        """Generate modular investor and management dashboard payloads."""
        logger.info("Building Commercial-View dashboard views")
        self.pipeline.load_all_datasets()

        portfolio_metrics = self.pipeline.compute_portfolio_metrics()
        recovery_metrics = self.pipeline.compute_recovery_metrics()
        executive_summary = self.pipeline.generate_executive_summary()

        risk_snapshot = self._build_risk_snapshot(portfolio_metrics)
        growth_indicators = self._build_growth_indicators(portfolio_metrics, recovery_metrics)
        operational_focus = self._build_operational_focus(portfolio_metrics)
        alerts = self._detect_operational_alerts(portfolio_metrics)

        snapshot = {
            "portfolio": portfolio_metrics,
            "risk": risk_snapshot,
            "growth": growth_indicators,
            "performance": recovery_metrics.head(5).to_dict("records")
            if recovery_metrics is not None and not recovery_metrics.empty
            else {},
            "operations": operational_focus,
            "alerts": alerts["alerts"],
        }

        investor_ai = self.ai_orchestrator.generate_investor_analysis(snapshot)
        executive_ai = self.ai_orchestrator.generate_summary(snapshot)
        operational_ai = self.ai_orchestrator.generate_operational_brief(snapshot)

        views = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "investor": {
                "headline_metrics": self._format_investor_metrics(portfolio_metrics, growth_indicators),
                "risk_highlights": risk_snapshot,
                "ai_commentary": investor_ai.__dict__,
                "narrative": investor_ai.text,
            },
            "management": {
                "operational_kpis": operational_focus,
                "ai_commentary": operational_ai.__dict__,
                "executive_summary": executive_summary,
            },
            "operational_alerts": alerts,
            "executive": {
                "ai_commentary": executive_ai.__dict__,
                "summary": executive_summary,
            },
        }

        logger.info("Dashboard views generated successfully")
        return views

    def export_dashboard_views(
        self,
        views: Dict[str, Any],
        *,
        export_to_figma: bool = True,
        export_to_slack: bool = True,
    ) -> Dict[str, Any]:
        """Export generated dashboard views to Figma and Slack."""
        logger.info(
            "Exporting dashboard views to destinations (figma=%s, slack=%s)",
            export_to_figma,
            export_to_slack,
        )
        return self.distributor.distribute(
            views,
            export_to_figma=export_to_figma,
            export_to_slack=export_to_slack,
        )

    def _create_pipeline(self) -> "CommercialViewPipeline":
        """Instantiate the CommercialViewPipeline with guard handling."""

        for module_name in ("pipeline", "src.pipeline"):
            try:
                module = importlib.import_module(module_name)
                pipeline_cls = getattr(module, "CommercialViewPipeline")
                return pipeline_cls()
            except SystemExit as exc:  # pragma: no cover - environment guard
                logger.error(
                    "Pipeline module exited during import. Ensure the project virtual "
                    "environment is activated before running orchestration."
                )
                raise RuntimeError(
                    "CommercialViewPipeline unavailable - activate the project virtual environment"
                ) from exc
            except (ModuleNotFoundError, AttributeError):
                continue

        raise RuntimeError("CommercialViewPipeline could not be located")

    def _build_risk_snapshot(self, portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        dpd_distribution = portfolio_metrics.get("dpd_distribution", {})
        npl_value = portfolio_metrics.get("npl_180", 0)
        outstanding = portfolio_metrics.get("portfolio_outstanding", 1)
        npl_ratio = (npl_value / outstanding * 100) if outstanding else 0
        top10 = portfolio_metrics.get("concentration_top10_pct", 0)
        max_single = portfolio_metrics.get("max_borrower_pct", 0)
        return {
            "dpd_distribution": dpd_distribution,
            "npl_ratio": round(npl_ratio, 2),
            "top_10_concentration_pct": round(top10, 2),
            "single_obligor_pct": round(max_single, 2),
        }

    def _build_growth_indicators(
        self,
        portfolio_metrics: Dict[str, Any],
        recovery_metrics,
    ) -> Dict[str, Any]:
        outstanding = portfolio_metrics.get("portfolio_outstanding", 0)
        active_clients = portfolio_metrics.get("active_clients", 0)
        weighted_apr = portfolio_metrics.get("weighted_apr", 0)
        recent_recovery = (
            recovery_metrics.sort_values("months_since_disbursement", ascending=False)
            .head(1)["recovery_pct"]
            if hasattr(recovery_metrics, "sort_values") and not recovery_metrics.empty
            else None
        )
        return {
            "portfolio_outstanding": round(outstanding, 2),
            "active_clients": active_clients,
            "weighted_apr": round(weighted_apr, 2),
            "latest_recovery_pct": round(float(recent_recovery.item()), 2)
            if recent_recovery is not None and not recent_recovery.empty
            else None,
        }

    def _build_operational_focus(self, portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        dpd_distribution = portfolio_metrics.get("dpd_distribution", {})
        severe_buckets = {
            bucket: value
            for bucket, value in dpd_distribution.items()
            if bucket in {"90d", "120d", "150d", "180d+"}
        }
        return {
            "collections_pressure": round(sum(severe_buckets.values()), 2)
            if severe_buckets
            else 0,
            "dpd_distribution": dpd_distribution,
        }

    def _detect_operational_alerts(self, portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        alerts = []
        summary_counts = {}

        npl_ratio = 0
        outstanding = portfolio_metrics.get("portfolio_outstanding", 0)
        npl_value = portfolio_metrics.get("npl_180", 0)
        if outstanding:
            npl_ratio = npl_value / outstanding * 100

        if npl_ratio > 8:
            alerts.append("NPL ratio exceeds 8% threshold")
            summary_counts["npl_ratio_pct"] = round(npl_ratio, 2)

        concentration = portfolio_metrics.get("max_borrower_pct", 0)
        if concentration > 15:
            alerts.append("Single obligor concentration above 15%")
            summary_counts["max_borrower_pct"] = round(concentration, 2)

        severe_dpd = sum(
            value
            for bucket, value in portfolio_metrics.get("dpd_distribution", {}).items()
            if bucket in {"90d", "120d", "150d", "180d+"}
        )
        if severe_dpd > 0.05 * outstanding:
            alerts.append("Severe DPD exposure greater than 5% of portfolio")
            summary_counts["severe_dpd_value"] = round(severe_dpd, 2)

        return {
            "alerts": alerts,
            "summary_counts": summary_counts,
            "critical": any("exceeds" in alert.lower() or "greater" in alert.lower() for alert in alerts),
        }

    def _format_investor_metrics(
        self,
        portfolio_metrics: Dict[str, Any],
        growth_indicators: Dict[str, Any],
    ) -> Dict[str, Any]:
        formatted = {
            "portfolio_outstanding": f"${growth_indicators.get('portfolio_outstanding', 0):,.2f}",
            "active_clients": growth_indicators.get("active_clients", 0),
            "weighted_apr": f"{growth_indicators.get('weighted_apr', 0):.2f}%",
            "npl_ratio": f"{self._safe_ratio(portfolio_metrics)}%",
        }
        if growth_indicators.get("latest_recovery_pct") is not None:
            formatted["latest_recovery_pct"] = f"{growth_indicators['latest_recovery_pct']:.2f}%"
        return formatted

    def _safe_ratio(self, portfolio_metrics: Dict[str, Any]) -> float:
        outstanding = portfolio_metrics.get("portfolio_outstanding", 0)
        if not outstanding:
            return 0.0
        return round(portfolio_metrics.get("npl_180", 0) / outstanding * 100, 2)


__all__ = ["DashboardOrchestrator"]
