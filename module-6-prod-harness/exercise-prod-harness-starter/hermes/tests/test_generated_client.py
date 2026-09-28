"""Behavioral test for the client generated in the Hermes harness run."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import unittest


DEFAULT_CLIENT = Path(__file__).resolve().parents[1] / "runs" / "src" / "xyz_api_client.py"


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

        result = module.connect_to_xyz_api()

        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "synced", result)
        self.assertIsInstance(result.get("sync_id"), str)
        self.assertTrue(result["sync_id"])
        self.assertIsInstance(result.get("timestamp"), str)
        self.assertTrue(result["timestamp"])
        self.assertIsInstance(result.get("received_client"), str)
        self.assertTrue(result["received_client"])
        self.assertIsInstance(result.get("payload_size"), int)


if __name__ == "__main__":
    unittest.main(verbosity=2)
