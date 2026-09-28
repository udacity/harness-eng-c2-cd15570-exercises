"""End-to-end checks for the supplied XYZ API server.

Start the server before running this file:

    python3 api_server/server.py
"""

from __future__ import annotations

import json
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://localhost:8080"


def request_json(
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    body: object | None = None,
) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers or {},
        method=method,
    )

    try:
        with urlopen(request, timeout=2) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)
    except URLError as error:
        raise AssertionError(
            "The XYZ API server is not available at http://localhost:8080. "
            "Start it with `python3 api_server/server.py` before running this test. "
            f"Original error: {error.reason}"
        ) from error


def valid_sync_headers() -> dict[str, str]:
    return {
        "Authorization": "Bearer xyz-jwt-server-test",
        "Content-Type": "application/json",
        "X-API-Version": "2026-03",
        "X-Client-ID": "api-server-test",
    }


class APIServerTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        status, response = request_json("GET", "/health")

        self.assertEqual(status, 200)
        self.assertEqual(response, {"status": "ok", "version": "2026-03"})

    def test_api_docs_endpoint_describes_data_sync_contract(self) -> None:
        status, response = request_json("GET", "/api-docs")

        self.assertEqual(status, 200)
        self.assertEqual(response["api"], "XYZ API")
        self.assertEqual(response["version"], "2026-03")
        self.assertEqual(response["token_prefix"], "xyz-jwt-")
        self.assertEqual(response["endpoints"]["data_sync"]["method"], "POST")
        self.assertEqual(
            response["endpoints"]["data_sync"]["path"], "/v2/data-sync"
        )

    def test_data_sync_endpoint_accepts_a_valid_request(self) -> None:
        status, response = request_json(
            "POST",
            "/v2/data-sync",
            headers=valid_sync_headers(),
            body={"client": "api-server-test", "payload": {"data": "sample data"}},
        )

        self.assertEqual(status, 200)
        self.assertEqual(response["status"], "synced")
        self.assertTrue(response["sync_id"])
        self.assertTrue(response["timestamp"].endswith("Z"))
        self.assertEqual(response["received_client"], "api-server-test")
        self.assertIsInstance(response["payload_size"], int)

    def test_data_sync_endpoint_rejects_invalid_requests(self) -> None:
        cases = [
            ({}, {"client": "test", "payload": {}}, 401),
            (
                {
                    **valid_sync_headers(),
                    "Authorization": "Bearer wrong-token-format",
                },
                {"client": "test", "payload": {}},
                401,
            ),
            (
                {
                    key: value
                    for key, value in valid_sync_headers().items()
                    if key != "X-Client-ID"
                },
                {"client": "test", "payload": {}},
                400,
            ),
            (
                {**valid_sync_headers(), "X-API-Version": "2025-01"},
                {"client": "test", "payload": {}},
                400,
            ),
            (valid_sync_headers(), {"client": "test"}, 400),
        ]

        for headers, body, expected_status in cases:
            with self.subTest(headers=headers, body=body):
                status, response = request_json(
                    "POST", "/v2/data-sync", headers=headers, body=body
                )

                self.assertEqual(status, expected_status)
                self.assertTrue(response["error"])

    def test_unknown_endpoint_returns_404(self) -> None:
        for method in ("GET", "POST"):
            with self.subTest(method=method):
                status, response = request_json(method, "/not-an-endpoint")

                self.assertEqual(status, 404)
                self.assertEqual(response, {"error": "Not Found"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
