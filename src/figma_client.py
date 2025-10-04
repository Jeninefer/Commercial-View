import os
import requests
from typing import Dict, Any

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
    return response.json()
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()
