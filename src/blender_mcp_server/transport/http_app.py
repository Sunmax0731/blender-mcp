from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

from ..services.command_store import claim_next_command
from ..services.command_store import submit_command_result
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
            payload = self._read_json_body()
            if payload is None:
                return

            updated = update_status_state(payload)
            self._send_json(HTTPStatus.OK, {"success": True, "data": updated})
            return

        if self.path == "/api/addon/command/poll":
            payload = self._read_json_body()
            if payload is None:
                return

            update_status_state(payload)
            command = claim_next_command()
            self._send_json(
                HTTPStatus.OK,
                {
                    "success": True,
                    "data": {
                        "command": command,
                    },
                },
            )
            return

        if self.path == "/api/addon/command-result":
            payload = self._read_json_body()
            if payload is None:
                return

            try:
                result = submit_command_result(payload)
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {
                        "success": False,
                        "error": {
                            "code": "INVALID_ARGUMENT",
                            "message": str(exc),
                        },
                    },
                )
                return

            self._send_json(HTTPStatus.OK, {"success": True, "data": result})
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

    def _read_json_body(self) -> dict[str, object] | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            return json.loads(raw_body.decode("utf-8")) if raw_body else {}
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
            return None

    def _send_json(self, status: HTTPStatus, payload: dict[str, object]):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def create_http_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), BlenderMcpHttpHandler)
