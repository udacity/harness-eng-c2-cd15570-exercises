"""Client for the local 2026 XYZ API."""

import requests
from requests.exceptions import RequestException, Timeout


def connect_to_xyz_api() -> dict:
    """Synchronize sample data with the local XYZ API and return its JSON result."""
    url = "http://localhost:8080/v2/data-sync"
    token = "xyz-jwt-sampletoken"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-API-Version": "2026-03",
        "X-Client-ID": "unique-client-id"
    }
    payload = {
        "client": "unique-client-id",
        "payload": {"sample": "data"}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        # Return JSON for both successful and rejection HTTP responses
        return response.json()
    except (RequestException, Timeout) as e:
        return {"error": str(e)}
