"""Dashboard export orchestrator for Commercial-View."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import figma_client
from slack_notifier import SlackNotifier

logger = logging.getLogger(__name__)


class DashboardDistributionManager:
    """Exports dashboard outputs to design (Figma) and operations (Slack)."""

    def __init__(
        self,
        *,
        figma_file_key: Optional[str] = None,
        slack_webhook_url: Optional[str] = None,
    ) -> None:
        self.figma_file_key = figma_file_key or os.getenv("FIGMA_FILE_KEY")
        self.slack_notifier = SlackNotifier(slack_webhook_url)

    def distribute(
        self,
        views: Dict[str, Any],
        *,
        export_to_figma: bool = True,
        export_to_slack: bool = True,
    ) -> Dict[str, Any]:
        """Export dashboard payload to the configured destinations."""
        results: Dict[str, Any] = {"figma": None, "slack": None, "errors": []}

        if export_to_figma:
            try:
                results["figma"] = self._export_to_figma(views)
            except Exception as exc:  # pragma: no cover - network failure
                logger.error("Failed to export dashboard to Figma: %s", exc)
                results["errors"].append({"destination": "figma", "error": str(exc)})

        if export_to_slack:
            try:
                results["slack"] = self._export_to_slack(views)
            except Exception as exc:  # pragma: no cover - network failure
                logger.error("Failed to export dashboard to Slack: %s", exc)
                results["errors"].append({"destination": "slack", "error": str(exc)})

        return results

    def _export_to_figma(self, views: Dict[str, Any]) -> Dict[str, Any]:
        if not self.figma_file_key:
            raise RuntimeError("FIGMA_FILE_KEY is not configured")

        investor = views.get("investor", {})
        management = views.get("management", {})

        message_lines = [
            "Commercial-View dashboard export",
            "Investor headline metrics:",
        ]
        for key, value in investor.get("headline_metrics", {}).items():
            message_lines.append(f"• {key.replace('_', ' ').title()}: {value}")
        message_lines.append("Management focus areas:")
        for key, value in management.get("operational_kpis", {}).items():
            message_lines.append(f"• {key.replace('_', ' ').title()}: {value}")

        payload = {
            "message": "\n".join(message_lines),
            "metadata": {
                "investor_view": investor,
                "management_view": management,
                "alerts": views.get("operational_alerts", {}),
            },
        }

        response = figma_client.post_figma_comment(
            file_key=self.figma_file_key,
            message=payload["message"],
            client_meta={"commercial_view": payload["metadata"]},
        )
        return {"status": "posted", "response": response, "payload": payload}

    def _export_to_slack(self, views: Dict[str, Any]) -> Dict[str, Any]:
        investor = views.get("investor", {})
        alerts = views.get("operational_alerts", {})

        summary = investor.get("ai_commentary", {}).get("text") or investor.get(
            "narrative", "No AI summary available"
        )

        metrics = {}
        metrics.update(investor.get("headline_metrics", {}))
        metrics.update(alerts.get("summary_counts", {}))

        return self.slack_notifier.send_dashboard_alert(
            title="Commercial-View Portfolio Update",
            summary=summary,
            metrics=metrics,
            priority="critical" if alerts.get("critical") else "info",
        )


__all__ = ["DashboardDistributionManager"]
