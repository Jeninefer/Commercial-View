"""
External Integrations Module for Commercial-View

Manages connections to external services including Slack, HubSpot, Figma,
and Zapier for automated reporting and notifications.
"""

import os
import logging
from typing import Dict, Any, Optional
import requests
from pathlib import Path

# Slack SDK
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    SLACK_SDK_AVAILABLE = True
except ImportError:
    WebClient = None
    SlackApiError = Exception
    SLACK_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constants
DEFAULT_SLACK_CHANNEL = "#general"
SLACK_API_URL = "https://slack.com/api/chat.postMessage"
HUBSPOT_API_BASE = "https://api.hubapi.com"
FIGMA_API_BASE = "https://api.figma.com/v1"
DEFAULT_TIMEOUT = 30


class SlackIntegration:
    """Slack messaging integration."""

    def __init__(self):
        """Initialize Slack client."""
        self.token = os.getenv("SLACK_BOT_TOKEN")
        self.client = self._initialize_client()

    def _initialize_client(self) -> Optional[WebClient]:
        """Initialize Slack WebClient if available."""
        if not self.token or not SLACK_SDK_AVAILABLE:
            return None

        try:
            client = WebClient(token=self.token)
            logger.info("✅ Slack client initialized")
            return client
        except Exception as e:
            logger.warning(f"Slack SDK init failed: {e}")
            return None

    def send_message(
        self, message: str, channel: Optional[str] = None, blocks: Optional[list] = None
    ) -> bool:
        """
        Send message to Slack channel.

        Args:
            message: Text message to send
            channel: Target channel (default from env or #general)
            blocks: Optional Block Kit blocks for rich formatting

        Returns:
            True if successful
        """
        if not self.token:
            logger.error("SLACK_BOT_TOKEN not set")
            return False

        target_channel = channel or os.getenv(
            "DEFAULT_OUTPUT_CHANNEL", DEFAULT_SLACK_CHANNEL
        )

        try:
            if self.client:
                return self._send_with_sdk(target_channel, message, blocks)
            return self._send_with_rest_api(target_channel, message, blocks)

        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False

    def _send_with_sdk(
        self, channel: str, message: str, blocks: Optional[list]
    ) -> bool:
        """Send message using Slack SDK."""
        self.client.chat_postMessage(channel=channel, text=message, blocks=blocks)
        logger.info(f"✅ Slack message sent to {channel}")
        return True

    def _send_with_rest_api(
        self, channel: str, message: str, blocks: Optional[list]
    ) -> bool:
        """Send message using REST API fallback."""
        response = requests.post(
            SLACK_API_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={"channel": channel, "text": message, "blocks": blocks},
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack API error: {data.get('error')}")

        logger.info(f"✅ Slack message sent to {channel}")
        return True

    def send_file(
        self,
        filepath: str,
        channel: Optional[str] = None,
        title: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> bool:
        """
        Upload file to Slack channel.

        Args:
            filepath: Path to file to upload
            channel: Target channel
            title: File title
            comment: Optional comment

        Returns:
            True if successful
        """
        if not self.client:
            logger.error("Slack client not initialized")
            return False

        target_channel = channel or os.getenv(
            "DEFAULT_OUTPUT_CHANNEL", DEFAULT_SLACK_CHANNEL
        )

        try:
            with open(filepath, "rb") as file_content:
                self.client.files_upload_v2(
                    channel=target_channel,
                    file=file_content,
                    title=title or Path(filepath).name,
                    initial_comment=comment,
                )

            logger.info(f"✅ File uploaded to Slack: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload file to Slack: {e}")
            return False


class HubSpotIntegration:
    """HubSpot CRM integration."""

    def __init__(self):
        """Initialize HubSpot client."""
        self.token = os.getenv("HUBSPOT_API_TOKEN")
        self.headers = (
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            if self.token
            else {}
        )

    def fetch_metrics(self) -> Dict[str, Any]:
        """
        Fetch marketing metrics from HubSpot.

        Returns:
            Dictionary with HubSpot metrics
        """
        if not self.token:
            logger.warning("HUBSPOT_API_TOKEN not set")
            return {}

        try:
            metrics = {}
            metrics.update(self._fetch_contacts_count())
            metrics.update(self._fetch_deals_count())
            metrics.update(self._fetch_companies_count())

            logger.info(f"✅ Fetched HubSpot metrics: {len(metrics)} metrics")
            return metrics

        except Exception as e:
            logger.error(f"Error fetching HubSpot metrics: {e}")
            return {}

    def _fetch_contacts_count(self) -> Dict[str, int]:
        """Fetch contacts count from HubSpot."""
        response = self._get("/crm/v3/objects/contacts", params={"limit": 1})
        if response:
            return {"total_contacts": response.get("total", 0)}
        return {}

    def _fetch_deals_count(self) -> Dict[str, int]:
        """Fetch deals count from HubSpot."""
        response = self._get("/crm/v3/objects/deals", params={"limit": 1})
        if response:
            return {"total_deals": response.get("total", 0)}
        return {}

    def _fetch_companies_count(self) -> Dict[str, int]:
        """Fetch companies count from HubSpot."""
        response = self._get("/crm/v3/objects/companies", params={"limit": 1})
        if response:
            return {"total_companies": response.get("total", 0)}
        return {}

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make GET request to HubSpot API."""
        try:
            url = f"{HUBSPOT_API_BASE}{endpoint}"
            response = requests.get(
                url, headers=self.headers, params=params, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HubSpot API request failed: {e}")
            return None


class FigmaIntegration:
    """Figma design integration."""

    def __init__(self):
        """Initialize Figma client."""
        self.token = os.getenv("FIGMA_API_TOKEN")
        self.file_id = os.getenv("FIGMA_FILE_ID")
        self.headers = {"X-Figma-Token": self.token} if self.token else {}

    def upload_chart(self, node_id: str, image_url: Optional[str] = None) -> bool:
        """
        Update Figma node with chart image.

        Note: Figma requires publicly accessible image URLs.
        Consider uploading to S3/CDN first.

        Args:
            node_id: Figma node ID to update
            image_url: Public URL of image (required)

        Returns:
            True if successful
        """
        if not self._validate_credentials():
            return False

        if not image_url:
            logger.error("image_url required for Figma upload")
            return False

        try:
            url = f"{FIGMA_API_BASE}/files/{self.file_id}/images"

            # Get node images
            response = requests.get(
                url,
                headers=self.headers,
                params={"ids": node_id, "scale": 1},
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()

            logger.info(f"✅ Figma chart upload initiated for node {node_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload to Figma: {e}")
            return False

    def _validate_credentials(self) -> bool:
        """Validate Figma credentials are present."""
        if not self.token or not self.file_id:
            logger.error("FIGMA_API_TOKEN or FIGMA_FILE_ID not set")
            return False
        return True


class ZapierIntegration:
    """Zapier webhook integration."""

    def __init__(self):
        """Initialize Zapier integration."""
        self.webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")

    def trigger_webhook(self, data: Dict[str, Any]) -> bool:
        """
        Trigger Zapier webhook with data payload.

        Args:
            data: Dictionary to send to Zapier

        Returns:
            True if successful
        """
        if not self.webhook_url:
            logger.warning("ZAPIER_WEBHOOK_URL not set")
            return False

        try:
            response = requests.post(
                self.webhook_url, json=data, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()

            logger.info("✅ Zapier webhook triggered successfully")
            return True

        except Exception as e:
            logger.error(f"Zapier webhook failed: {e}")
            return False


# Convenience functions
def send_slack_message(message: str, channel: Optional[str] = None) -> bool:
    """Send message to Slack."""
    slack = SlackIntegration()
    return slack.send_message(message, channel)


def fetch_hubspot_metrics() -> Dict[str, Any]:
    """Fetch metrics from HubSpot."""
    hubspot = HubSpotIntegration()
    return hubspot.fetch_metrics()


def upload_chart_to_figma(node_id: str, image_url: str) -> bool:
    """Upload chart to Figma."""
    figma = FigmaIntegration()
    return figma.upload_chart(node_id, image_url)


def trigger_zapier_webhook(data: Dict[str, Any]) -> bool:
    """Trigger Zapier webhook."""
    zapier = ZapierIntegration()
    return zapier.trigger_webhook(data)
