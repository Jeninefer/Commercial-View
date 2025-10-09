"""Slack notification utilities for Commercial-View dashboards."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Dispatches structured dashboard alerts to Slack via webhook."""

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            logger.warning("SlackNotifier initialized without webhook URL")

    def send_dashboard_alert(
        self,
        *,
        title: str,
        summary: str,
        metrics: Dict[str, Any],
        priority: str = "info",
    ) -> Dict[str, Any]:
        """Send a dashboard alert message to Slack."""
        if not self.webhook_url:
            raise RuntimeError("Slack webhook URL is not configured")

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": title[:150]},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Priority:* {priority.capitalize()}\n{summary}",
                },
            },
        ]

        if metrics:
            metrics_table = "\n".join(
                f"• *{key.replace('_', ' ').title()}:* {value}" for key, value in metrics.items()
            )
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": metrics_table[:2900]},
                }
            )

        payload = {"blocks": blocks, "text": summary, "attachments": []}

        response = requests.post(self.webhook_url, json=payload, timeout=10)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - network failure
            logger.error("Slack notification failed: %s", exc)
            raise

        return {"status": "sent", "status_code": response.status_code, "payload": payload}


__all__ = ["SlackNotifier"]
