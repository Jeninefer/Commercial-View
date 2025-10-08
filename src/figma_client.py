import os
import requests
from typing import Dict, Any, Optional

FIGMA_API_BASE_URL = "https://api.figma.com/v1/"


def _build_headers() -> Dict[str, str]:
    token = os.getenv("FIGMA_TOKEN")
    if not token:
        raise RuntimeError("FIGMA_TOKEN environment variable not set.")
    return {"X-Figma-Token": token}


def get_figma_file(file_key: str) -> Dict[str, Any]:
    url = f"{FIGMA_API_BASE_URL}files/{file_key}"
    response = requests.get(url, headers=_build_headers())
    response.raise_for_status()
    # Add logging here if additional diagnostics are required.
    return response.json()


def post_figma_comment(
    *, file_key: str, message: str, client_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Post a structured comment to a Figma file for design review."""

    url = f"{FIGMA_API_BASE_URL}files/{file_key}/comments"
    payload: Dict[str, Any] = {"message": message}
    if client_meta:
        payload["client_meta"] = client_meta

    response = requests.post(url, headers=_build_headers(), json=payload)
    response.raise_for_status()
    return response.json()


__all__ = ["get_figma_file", "post_figma_comment"]
