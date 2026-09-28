"""Maintainer reference implementation of the 2026 XYZ API client.

The harness agent discovers the contract before producing this client. The
generated client itself only performs the data-synchronization operation.
"""

import requests
from datetime import datetime, timezone


def connect_to_xyz_api() -> dict:
    """Connect to the 2026 XYZ API and sync data.

    The agent learned the required endpoint, headers, and body format from the
    local documentation endpoint before writing this implementation.
    """
    base_url = "http://localhost:8080"

    auth_token = "xyz-jwt-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.payload.signature"
    client_id = "xyz-client-001"

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "X-API-Version": "2026-03",
        "X-Client-ID": client_id,
    }

    payload = {
        "client": client_id,
        "payload": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": "sample_data_for_sync",
            "source": "harness_agent",
        },
    }

    try:
        response = requests.post(
            f"{base_url}/v2/data-sync",
            headers=headers,
            json=payload,
            timeout=10
        )

        return response.json()
    except requests.RequestException as error:
        return {"error": str(error)}
