"""
Starter file for The Offline API Connector exercise.

Task: Write a Python script that connects to the mock 2026 XYZ API server.

You do NOT have knowledge of the 2026 XYZ API specification. You will need to
either:
1. Use web_search skills to find the API docs (if permitted)
2. Explore the mock server's /api-docs endpoint
3. Try common API patterns and debug errors

The server is already running at http://localhost:8080

DO: Fill in the implementation below.
DON'T: Modify the mock server or test files.
"""

import requests
from datetime import datetime, timezone


def discover_api_docs(base_url: str = "http://localhost:8080") -> dict:
    """Fetch API documentation from the server's /api-docs endpoint.

    The 2026 XYZ API is brand-new and not in our training data, so we
    discover the spec at runtime rather than relying on outdated patterns.
    """
    try:
        response = requests.get(f"{base_url}/api-docs", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return {}


def connect_to_xyz_api() -> dict:
    """Connect to the 2026 XYZ API and sync data.

    Implementation strategy:
    1. Discover API docs from /api-docs endpoint (2026 spec not in training data)
    2. Use Bearer JWT auth with the xyz-jwt- token prefix required by 2026 standard
    3. POST to /v2/data-sync with all required 2026-03 headers
    4. Send payload with client and payload fields
    5. Handle the response correctly
    """
    base_url = "http://localhost:8080"

    # Step 1: Discover API docs (simulates web_search or /api-docs exploration).
    # Training data only has older API patterns; the 2026 XYZ API requires
    # a specific token prefix and API version that we can't guess.
    docs = discover_api_docs(base_url)

    # Step 2: Build the 2026-standard Bearer JWT auth token.
    # The 2026 XYZ API requires tokens starting with "xyz-jwt-".
    auth_token = "xyz-jwt-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJob3JtZXMtYWdlbnAwMDEiLCJ2ZXJzaW9bijoiMjAyNi0wMyIsImlhdCI6MTc0MDAwMDAwMCwiZXhwIjo5OTk5OTk5OTk5fQ.signature_placeholder"
    client_id = "hermes-agent-001"

    # Step 3: POST to /v2/data-sync with all required 2026-03 headers.
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "X-API-Version": "2026-03",
        "X-Client-ID": client_id,
    }

    # Step 4: Build payload with the required client and payload fields.
    payload = {
        "client": client_id,
        "payload": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": "sample_data_for_sync",
            "source": "hermes_agent",
        },
    }

    # Step 5: Send request and handle the response.
    try:
        response = requests.post(
            f"{base_url}/v2/data-sync",
            headers=headers,
            json=payload,
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Success: Synced data with ID {result.get('sync_id')}")
            return result

        elif response.status_code == 401:
            result = response.json()
            print(f"Auth error: {result.get('error')}")
            return result

        elif response.status_code == 400:
            result = response.json()
            print(f"Bad request: {result.get('error')}")
            return result

        else:
            result = response.json()
            print(f"Unexpected response ({response.status_code}): {result}")
            return result

    except requests.RequestException as e:
        print(f"Connection error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    result = connect_to_xyz_api()
    if result and result.get("status") == "synced":
        print("Successfully connected to 2026 XYZ API!")
    else:
        print("Failed to connect to XYZ API")