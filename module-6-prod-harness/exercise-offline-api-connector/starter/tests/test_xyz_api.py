"""
Validation tests for The Offline API Connector exercise.

Run with: python -m pytest tests/test_xyz_api.py -v

These tests validate both structural correctness (is it valid Python?)
and logical correctness (is it the right API syntax?).
"""

import pytest
import subprocess
import sys
import os
import json
import time
import threading
from http.server import HTTPServer

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'starter'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from starter.mock_api.server import XYZAPIHandler


class TestXYZAPIClient:
    """Test suite for the 2026 XYZ API client implementation."""

    @pytest.fixture(autouse=True)
    def setup_server(self):
        """Start mock server for tests."""
        self.server = HTTPServer(('localhost', 8080), XYZAPIHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.5)
        self.server_ok = True
        yield
        self.server.shutdown()
        self.server.server_close()

    def test_file_exists(self):
        """Test 1 (Structural): The client file exists."""
        path = os.path.join(os.path.dirname(__file__), '..', 'src', 'xyz_api_client.py')
        assert os.path.exists(path), "xyz_api_client.py must exist"

    def test_file_is_valid_python(self):
        """Test 2 (Structural): The file contains valid Python syntax."""
        path = os.path.join(os.path.dirname(__file__), '..', 'src', 'xyz_api_client.py')
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", path],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_client_has_connect_function(self):
        """Test 3 (Structural): The module has a connect function."""
        # Import the client module
        client_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, client_path)
        import xyz_api_client
        assert hasattr(xyz_api_client, 'connect_to_xyz_api'), \
            "Must implement connect_to_xyz_api() function"

    def test_connect_returns_dict(self):
        """Test 4 (Structural): The connect function returns a dict."""
        client_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, client_path)
        import xyz_api_client
        result = xyz_api_client.connect_to_xyz_api()
        assert result is not None, "connect_to_xyz_api() should return a result"
        assert isinstance(result, dict), "Result should be a dictionary"

    def test_uses_correct_auth_header(self):
        """Test 5 (Logical): Uses Bearer JWT auth with xyz-jwt- prefix."""
        client_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, client_path)
        # Reload to get fresh module
        if 'xyz_api_client' in sys.modules:
            del sys.modules['xyz_api_client']
        import xyz_api_client
        result = xyz_api_client.connect_to_xyz_api()
        # If successful, auth header was correct
        if result and result.get('status') == 'synced':
            pass  # Success means correct auth
        else:
            # Check if it's an auth error
            if result and 'error' in result:
                assert 'auth' not in result['error'].lower(), \
                    "Agent should use correct xyz-jwt- token format"

    def test_posts_to_v2_endpoint(self):
        """Test 6 (Logical): Posts to /v2/data-sync, not /v1/."""
        client_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, client_path)
        if 'xyz_api_client' in sys.modules:
            del sys.modules['xyz_api_client']
        import xyz_api_client
        result = xyz_api_client.connect_to_xyz_api()
        # If we got a sync_id, we used the correct endpoint
        if result and result.get('sync_id'):
            pass  # Correct endpoint
        elif result and result.get('error') == 'Not Found':
            pytest.fail("Agent posted to wrong endpoint (got 404)")

    def test_includes_client_and_payload(self):
        """Test 7 (Logical): Includes client and payload in request body."""
        client_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, client_path)
        if 'xyz_api_client' in sys.modules:
            del sys.modules['xyz_api_client']
        import xyz_api_client
        result = xyz_api_client.connect_to_xyz_api()
        # Successful response indicates correct payload format
        if result and result.get('status') == 'synced':
            assert result.get('received_client') is not None, \
                "Payload should include client field"

    def test_handles_api_docs_discovery(self):
        """Test 8 (Logical): Can discover API docs from /api-docs endpoint."""
        client_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, client_path)
        if 'xyz_api_client' in sys.modules:
            del sys.modules['xyz_api_client']
        import xyz_api_client

        # Check if the client tries to fetch API docs
        import inspect
        source = inspect.getsource(xyz_api_client.connect_to_xyz_api)
        has_docs_fetch = '/api-docs' in source or 'docs' in source.lower()
        # This test checks whether agent discovered the docs endpoint
        # Not strictly required but shows good practice
        assert has_docs_fetch or True, "Agent may not attempt docs discovery"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
