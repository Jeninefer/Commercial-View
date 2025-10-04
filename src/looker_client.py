import os
import requests

LOOKER_BASE_URL = os.getenv("LOOKER_BASE_URL")
LOOKER_CLIENT_ID = os.getenv("LOOKER_CLIENT_ID")
LOOKER_CLIENT_SECRET = os.getenv("LOOKER_CLIENT_SECRET")

class LookerClient:
    def __init__(self):
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        if not all([LOOKER_BASE_URL, LOOKER_CLIENT_ID, LOOKER_CLIENT_SECRET]):
            raise ValueError("Looker API credentials are not fully set in the environment variables.")
        
        auth_url = f"{LOOKER_BASE_URL}/api/4.0/login"
        payload = {
            "client_id": LOOKER_CLIENT_ID,
            "client_secret": LOOKER_CLIENT_SECRET
        }
        response = self.session.post(auth_url, data=payload)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        self.session.headers.update({"Authorization": f"token {access_token}"})

    def get_dashboard(self, dashboard_id: str):
        """Fetches a Looker dashboard by its ID."""
        url = f"{LOOKER_BASE_URL}/api/4.0/dashboards/{dashboard_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_look(self, look_id: str):
        """Fetches a Looker Look by its ID."""
        url = f"{LOOKER_BASE_URL}/api/4.0/looks/{look_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
