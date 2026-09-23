"""
Mock 2026 XYZ API Server

Simulates the brand-new XYZ API with 2026-standard authentication and endpoints.
DO NOT MODIFY THIS FILE - it represents the ground truth API specification.

API Specification (2026 Standard):
- Base URL: http://localhost:8080
- Auth: Bearer JWT tokens with prefix "xyz-jwt-"
- Endpoint: POST /v2/data-sync
- Headers required: 
  - Authorization: Bearer xyz-jwt-{token}
  - Content-Type: application/json
  - X-API-Version: 2026-03
  - X-Client-ID: required
- Payload: {"client": string, "payload": object}
- Response: {"status": "synced", "sync_id": string, "timestamp": iso_string}
- Error: Returns 401 for invalid/malformed auth headers
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime


class XYZAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default logging

    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        if self.path != '/v2/data-sync':
            self.send_json_response(404, {"error": "Not Found"})
            return

        # Validate authentication header
        auth_header = self.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            self.send_json_response(401, {"error": "Missing or malformed Authorization header"})
            return

        token = auth_header[7:]  # Remove "Bearer " prefix

        # 2026 XYZ API requires tokens starting with "xyz-jwt-"
        if not token.startswith('xyz-jwt-'):
            self.send_json_response(401, {"error": "Invalid token format. Expected xyz-jwt-*"})
            return

        # Validate required headers
        client_id = self.headers.get('X-Client-ID', '')
        api_version = self.headers.get('X-API-Version', '')

        if not client_id:
            self.send_json_response(400, {"error": "Missing X-Client-ID header"})
            return

        if api_version != '2026-03':
            self.send_json_response(400, {"error": f"Unsupported API version. Required: 2026-03, Got: {api_version}"})
            return

        # Parse request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_json_response(400, {"error": "Invalid JSON body"})
            return

        if 'client' not in payload or 'payload' not in payload:
            self.send_json_response(400, {"error": "Missing 'client' or 'payload' fields"})
            return

        # Success response with 2026 XYZ API format
        response = {
            "status": "synced",
            "sync_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "received_client": payload["client"],
            "payload_size": len(str(payload["payload"]))
        }
        self.send_json_response(200, response)

    def do_GET(self):
        if self.path == '/health':
            self.send_json_response(200, {"status": "ok", "version": "2026-03"})
        elif self.path == '/api-docs':
            # Return real API docs for agents that successfully fetch them
            docs = {
                "api": "XYZ API",
                "version": "2026-03",
                "authentication": "Bearer JWT tokens",
                "token_prefix": "xyz-jwt-",
                "endpoints": {
                    "data_sync": {
                        "method": "POST",
                        "path": "/v2/data-sync",
                        "required_headers": [
                            "Authorization: Bearer xyz-jwt-*",
                            "Content-Type: application/json",
                            "X-API-Version: 2026-03",
                            "X-Client-ID: <unique_string>"
                        ],
                        "payload_format": {
                            "client": "string - identifier for the client",
                            "payload": "object - data to sync"
                        },
                        "response": {
                            "status": "synced",
                            "sync_id": "uuid-string",
                            "timestamp": "ISO-8601 timestamp"
                        }
                    }
                },
                "common_errors": {
                    "401": "Invalid or missing authentication",
                    "400": "Missing required headers or malformed payload",
                    "404": "Endpoint not found"
                }
            }
            self.send_json_response(200, docs)
        else:
            self.send_json_response(404, {"error": "Not Found"})


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), XYZAPIHandler)
    print("Mock 2026 XYZ API Server running on http://localhost:8080")
    print("Endpoints:")
    print("  GET  /health       - Health check")
    print("  GET  /api-docs     - API documentation (fetchable)")
    print("  POST /v2/data-sync - Data sync endpoint")
    print("\nPress Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
