"""Behavioral test for the client generated in the Python harness run."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import unittest


DEFAULT_CLIENT = Path(__file__).resolve().parents[1] / "runs" / "src" / "xyz_api_client.py"
DEFAULT_REQUEST_LOG = (
    Path(__file__).resolve().parents[2] / "api_server" / "requests.jsonl"
)


def load_request_records() -> list[dict]:
    configured = os.environ.get("XYZ_API_REQUEST_LOG", "").strip()
    path = (
        Path(configured).expanduser().resolve()
        if configured
        else DEFAULT_REQUEST_LOG.resolve()
    )
    if not path.is_file():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise AssertionError(
                f"Invalid XYZ API request record at {path}:{line_number}: {error}"
            ) from error
        if not isinstance(record, dict):
            raise AssertionError(
                f"XYZ API request record at {path}:{line_number} is not an object."
            )
        records.append(record)
    return records


def load_generated_client():
    client_path = Path(os.environ.get("XYZ_CLIENT_PATH", DEFAULT_CLIENT)).resolve()
    if not client_path.is_file():
        raise AssertionError(f"Generated client does not exist: {client_path}")
    spec = importlib.util.spec_from_file_location("generated_xyz_api_client", client_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load generated client: {client_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeneratedClientTests(unittest.TestCase):
    def test_connect_to_xyz_api_synchronizes_data(self) -> None:
        module = load_generated_client()
        self.assertTrue(callable(getattr(module, "connect_to_xyz_api", None)))
        initial_record_count = len(load_request_records())

        result = module.connect_to_xyz_api()

        new_records = load_request_records()[initial_record_count:]
        self.assertEqual(
            len(new_records),
            1,
            "Expected exactly one new request recorded by the supplied XYZ API server. "
            "Restart the server if it was started before request journaling was enabled.",
        )
        request = new_records[0]
        self.assertEqual(request.get("method"), "POST")
        self.assertEqual(request.get("path"), "/v2/data-sync")
        self.assertEqual(request.get("status"), 200)

        headers = request.get("headers")
        self.assertIsInstance(headers, dict)
        authorization = headers.get("authorization", "")
        self.assertTrue(
            authorization.startswith("Bearer xyz-jwt-")
            and len(authorization) > len("Bearer xyz-jwt-")
        )
        self.assertEqual(headers.get("x-api-version"), "2026-03")
        self.assertTrue(headers.get("x-client-id", "").strip())
        self.assertEqual(
            headers.get("content-type", "").split(";", 1)[0].strip().lower(),
            "application/json",
        )

        body = request.get("body")
        self.assertIsInstance(body, dict)
        self.assertIsInstance(body.get("client"), str)
        self.assertTrue(body["client"].strip())
        self.assertIsInstance(body.get("payload"), dict)
        self.assertTrue(body["payload"])

        self.assertIsInstance(result, dict)
        self.assertEqual(result, request.get("response"))
        self.assertEqual(result.get("status"), "synced", result)
        self.assertIsInstance(result.get("sync_id"), str)
        self.assertTrue(result["sync_id"])
        self.assertIsInstance(result.get("timestamp"), str)
        self.assertTrue(result["timestamp"])
        self.assertIsInstance(result.get("received_client"), str)
        self.assertTrue(result["received_client"])
        self.assertIsInstance(result.get("payload_size"), int)
        self.assertEqual(result["received_client"], body["client"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
