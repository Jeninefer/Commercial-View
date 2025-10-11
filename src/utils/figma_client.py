"""
Figma API Client for Commercial-View Dashboard Integration
Supports dashboard design and visualization for Abaco loan tape analytics
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json


@dataclass
class FigmaProject:
    """Represents a Figma project for Commercial-View dashboards."""

    id: str
    name: str
    thumbnail_url: Optional[str] = None
    last_modified: Optional[str] = None


@dataclass
class FigmaNode:
    """Represents a Figma design node for dashboard components."""

    id: str
    name: str
    type: str
    children: Optional[List["FigmaNode"]] = None


class FigmaClient:
    """
    Figma API client for Commercial-View dashboard integration.

    Supports creating and managing dashboard designs for Abaco loan analytics,
    including Spanish language support and USD factoring visualizations.
    """

    BASE_URL = "https://api.figma.com/v1/"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize Figma client.

        Args:
            token: Figma API token. If None, reads from FIGMA_TOKEN environment variable.
        """
        self.token = token or os.getenv("FIGMA_TOKEN")
        if not self.token:
            raise RuntimeError(
                "FIGMA_TOKEN environment variable not set or token not provided."
            )
        self.headers = self._build_headers()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers for Figma API."""
        return {"X-Figma-Token": self.token, "Content-Type": "application/json"}

    def get_file(self, file_key: str) -> Dict[str, Any]:
        """
        Retrieve a Figma file for Commercial-View dashboards.

        Args:
            file_key: Figma file key for dashboard designs

        Returns:
            Dict containing file information and design nodes
        """
        url = f"{self.BASE_URL}files/{file_key}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to retrieve Figma file {file_key}: {e}")

    def get_team_projects(self, team_id: str) -> List[FigmaProject]:
        """
        Get Commercial-View dashboard projects from a Figma team.

        Args:
            team_id: Figma team ID containing dashboard projects

        Returns:
            List of FigmaProject instances for Commercial-View dashboards
        """
        url = f"{self.BASE_URL}teams/{team_id}/projects"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            projects = []
            for project_data in data.get("projects", []):
                project = FigmaProject(id=project_data["id"], name=project_data["name"])
                projects.append(project)

            return projects
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to retrieve team projects: {e}")

    def export_dashboard_image(
        self,
        file_key: str,
        node_ids: List[str],
        format: str = "png",
        scale: float = 2.0,
    ) -> Dict[str, str]:
        """
        Export dashboard components as images for Commercial-View reports.

        Useful for generating static images of Abaco analytics dashboards
        for regulatory reports and executive presentations.

        Args:
            file_key: Figma file key containing dashboard designs
            node_ids: List of node IDs to export (dashboard components)
            format: Export format ('png', 'jpg', 'svg', 'pdf')
            scale: Scale factor for export (1.0-4.0)

        Returns:
            Dict mapping node IDs to export URLs
        """
        url = f"{self.BASE_URL}images/{file_key}"
        params = {"ids": ",".join(node_ids), "format": format, "scale": scale}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("err"):
                raise RuntimeError(f"Figma export error: {data['err']}")

            return data.get("images", {})
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to export dashboard images: {e}")

    def get_dashboard_components(self, file_key: str) -> List[FigmaNode]:
        """
        Extract dashboard components from a Figma file.

        Specifically looks for Commercial-View dashboard elements like:
        - Abaco loan portfolio summaries
        - Spanish client name displays
        - USD factoring analytics charts
        - Risk scoring visualizations

        Args:
            file_key: Figma file key for dashboard analysis

        Returns:
            List of FigmaNode instances representing dashboard components
        """
        file_data = self.get_file(file_key)
        document = file_data.get("document", {})

        components = []
        self._extract_dashboard_nodes(document, components)

        return components

    def _extract_dashboard_nodes(
        self, node: Dict[str, Any], components: List[FigmaNode]
    ) -> None:
        """
        Recursively extract dashboard nodes from Figma document tree.

        Identifies Commercial-View specific components:
        - Portfolio summary cards
        - Risk scoring gauges
        - Payment status charts
        - Spanish language text elements

        Args:
            node: Current node in document tree
            components: List to accumulate dashboard components
        """
        node_name = node.get("name", "")
        node_type = node.get("type", "")

        # Check if this is a Commercial-View dashboard component
        dashboard_keywords = [
            "portfolio",
            "loan",
            "risk",
            "payment",
            "abaco",
            "factoring",
            "spanish",
            "usd",
            "analytics",
            "dashboard",
            "chart",
            "graph",
            "summary",
            "kpi",
        ]

        if any(keyword in node_name.lower() for keyword in dashboard_keywords):
            figma_node = FigmaNode(
                id=node.get("id", ""), name=node_name, type=node_type
            )
            components.append(figma_node)

        # Recursively check children
        for child in node.get("children", []):
            self._extract_dashboard_nodes(child, components)

    def create_commercial_view_template(
        self, team_id: str, project_name: str
    ) -> Dict[str, Any]:
        """
        Create a new Figma project template for Commercial-View dashboards.

        Sets up a standardized template with:
        - Abaco loan portfolio layouts
        - Spanish language text styles
        - USD currency formatting
        - Risk scoring color schemes
        - Executive summary templates

        Args:
            team_id: Figma team ID for the new project
            project_name: Name for the Commercial-View dashboard project

        Returns:
            Dict containing the new project information
        """
        # Note: Figma API doesn't support creating files via API
        # This would typically be done through Figma's web interface
        # or by duplicating existing templates

        template_info = {
            "team_id": team_id,
            "project_name": project_name,
            "template_type": "commercial_view_dashboard",
            "components": [
                "Abaco Portfolio Summary",
                "Spanish Client Directory",
                "USD Factoring Analytics",
                "Risk Scoring Dashboard",
                "Payment Status Overview",
                "Executive Summary Report",
            ],
            "color_scheme": {
                "primary": "#2E5BBA",  # Professional blue
                "secondary": "#28A745",  # Success green
                "warning": "#FFC107",  # Warning yellow
                "danger": "#DC3545",  # Error red
                "abaco_brand": "#1B365D",  # Abaco brand color
            },
            "typography": {
                "headers": "Inter Bold",
                "body": "Inter Regular",
                "spanish_text": "Inter Regular (UTF-8 supported)",
                "numbers": "Inter Medium (USD formatting)",
            },
        }

        return template_info


class CommercialViewDashboardBuilder:
    """
    Helper class for building Commercial-View dashboard components in Figma.

    Provides utilities for creating dashboard elements specifically designed
    for Abaco loan tape analytics with Spanish language support.
    """

    def __init__(self, figma_client: FigmaClient):
        """
        Initialize dashboard builder.

        Args:
            figma_client: Configured FigmaClient instance
        """
        self.figma = figma_client

    def generate_abaco_dashboard_spec(self) -> Dict[str, Any]:
        """
        Generate specifications for Abaco loan analytics dashboard.

        Creates a comprehensive specification for dashboard components
        that display the 48,853 record Abaco dataset with Spanish client
        names and USD factoring products.

        Returns:
            Dict containing complete dashboard specification
        """
        return {
            "dashboard_title": "Commercial-View: Abaco Loan Analytics",
            "data_source": "Abaco Loan Tape (48,853 records)",
            "language_support": ["English", "Spanish"],
            "currency": "USD",
            "product_focus": "Factoring",
            "components": {
                "portfolio_summary": {
                    "title": "Portfolio Overview",
                    "spanish_title": "Resumen de Cartera",
                    "metrics": [
                        "Total Loans: 48,853",
                        "Total Exposure: $XXX.XX MM USD",
                        "Spanish Clients: XX,XXX",
                        "Factoring Products: 100%",
                        "Avg Risk Score: X.XXX",
                    ],
                },
                "spanish_clients": {
                    "title": "Spanish Client Analytics",
                    "spanish_title": "Análisis de Clientes Españoles",
                    "sample_names": [
                        "SERVICIOS TECNICOS MEDICOS, S.A. DE C.V.",
                        "PRODUCTOS DE CONCRETO, S.A. DE C.V.",
                        "HOSPITAL NACIONAL SAN JUAN DE DIOS",
                    ],
                    "encoding": "UTF-8",
                },
                "factoring_analytics": {
                    "title": "USD Factoring Performance",
                    "spanish_title": "Rendimiento de Factoring USD",
                    "metrics": [
                        "Interest Rate Range: 29.47% - 36.99% APR",
                        "Payment Frequency: Bullet",
                        "Currency: USD Exclusively",
                        "Companies: Abaco Technologies & Financial",
                    ],
                },
                "risk_dashboard": {
                    "title": "Risk Analytics",
                    "spanish_title": "Análisis de Riesgo",
                    "buckets": [
                        "Current",
                        "Early Delinquent",
                        "Moderate Delinquent",
                        "Late Delinquent",
                        "Severe Delinquent",
                        "Default",
                        "NPL",
                    ],
                    "score_range": "0.0 - 1.0",
                },
            },
            "layout": {
                "grid": "12-column responsive",
                "breakpoints": ["mobile", "tablet", "desktop", "large"],
                "spacing": "8px base unit",
            },
        }


# Example usage and integration with Commercial-View
if __name__ == "__main__":
    # This would typically be used in a dashboard generation script
    print("Figma Client for Commercial-View Dashboard Integration")
    print("Supports Abaco loan analytics with Spanish language support")
    print("Ready for 48,853 record dataset visualization")
