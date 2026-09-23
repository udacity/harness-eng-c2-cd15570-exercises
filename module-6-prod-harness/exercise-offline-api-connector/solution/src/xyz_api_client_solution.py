"""
Solution: The Offline API Connector

This is the reference solution that correctly implements the 2026 XYZ API client.
It discovers API docs from the mock server's /api-docs endpoint and implements
the correct authentication and endpoint patterns.
"""

import requests
import json
from datetime import datetime


def discover_api_docs(base_url: str = "http://localhost:8080") -> dict:
    """Fetch API documentation from the /api-docs endpoint.

    This simulates the agent discovering API specs by:
    1. Recognizing knowledge gap (2026 API not in training data)
    2. Using web_search skill OR exploring the server's /api-docs endpoint
    3. Adapting implementation based on discovered specs
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

    This implementation:
    1. Discovers API docs from /api-docs endpoint
    2. Uses Bearer JWT auth with xyz-jwt- token prefix
    3. POSTs to /v2/data-sync with correct headers
    4. Sends payload with client and payload fields
    """
    base_url = "http://localhost:8080"

    # Step 1: Discover API docs (simulates web_search or exploration)
    docs = discover_api_docs(base_url)

    # Step 2: Build correct 2026 XYZ API request
    # Token format: xyz-jwt-{token} (2026 standard JWT prefix)
    auth_token = "xyz-jwt-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.payload.signature"
    client_id = "hermes-agent-001"

    # Step 3: Make the POST request with correct headers
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "X-API-Version": "2026-03",  # 2026 XYZ API version
        "X-Client-ID": client_id,
    }

    # Step 4: Build payload with required fields
    payload = {
        "client": client_id,
        "payload": {
            "timestamp": datetime.utcnow().isoformat(),
            "data": "sample_data_for_sync",
            "source": "hermes_agent"
        }
    }

    # Step 5: Send request and handle response
    try:
        response = requests.post(
            f"{base_url}/v2/data-sync",
            headers=headers,
            json=payload,
            timeout=10
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
        print("✓ Successfully connected to 2026 XYZ API!")
    else:
        print("✗ Failed to connect to XYZ API")
