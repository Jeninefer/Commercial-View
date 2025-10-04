import os
import requests

FIGMA_API_BASE_URL = "https://api.figma.com/v1/"
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")

if not FIGMA_TOKEN:
    raise ValueError("FIGMA_TOKEN environment variable not set.")

headers = {
    "X-Figma-Token": FIGMA_TOKEN
}

def get_figma_file(file_key: str):
    """Fetches a Figma file by its key."""
    url = f"{FIGMA_API_BASE_URL}files/{file_key}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()
