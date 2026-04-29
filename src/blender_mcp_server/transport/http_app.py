from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

from ..services.status_service import build_status_payload
from ..services.status_store import update_status_state


class BlenderMcpHttpHandler(BaseHTTPRequestHandler):
    server_version = "BlenderMcpHttp/0.1"

    def do_GET(self):
        if self.path == "/health":
            self._send_json(HTTPStatus.OK, {"ok": True})
            return

        if self.path == "/api/status":
            self._send_json(HTTPStatus.OK, build_status_payload())
            return

        self._send_json(
            HTTPStatus.NOT_FOUND,
            {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Requested endpoint was not found.",
                },
            },
        )

    def do_POST(self):
        if self.path == "/api/addon/status":
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            try:
                payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            except json.JSONDecodeError:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "success": False,
                        "error": {
                            "code": "INVALID_ARGUMENT",
                            "message": "Request body must be valid JSON.",
                        },
                    },
                )
                return

            updated = update_status_state(payload)
            self._send_json(HTTPStatus.OK, {"success": True, "data": updated})
            return

        self._send_json(
            HTTPStatus.NOT_FOUND,
            {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Requested endpoint was not found.",
                },
            },
        )

    def log_message(self, format, *args):
        return

    def _send_json(self, status: HTTPStatus, payload: dict[str, object]):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def create_http_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), BlenderMcpHttpHandler)
