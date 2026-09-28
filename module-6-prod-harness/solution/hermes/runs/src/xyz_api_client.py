"""Client for the local 2026 XYZ API."""

import json
import urllib.error
import urllib.request
import uuid


def connect_to_xyz_api() -> dict:
    """Synchronize sample data with the local XYZ API and return its JSON result."""

    url = "http://localhost:8080/v2/data-sync"
    timeout = 30

    token = f"xyz-jwt-{uuid.uuid4().hex}"
    client_id = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-API-Version": "2026-03",
        "X-Client-ID": client_id,
    }

    body = json.dumps({
        "client": "xyz-api-client",
        "payload": {
            "sync_type": "sample",
            "data": "hello",
        },
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # Return parsed JSON for rejected HTTP responses (4xx/5xx)
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            return {"error": f"HTTP {e.code}: {e.reason}"}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # Convert connection and timeout failures into a dictionary
        return {"error": f"Connection error: {e}"}
