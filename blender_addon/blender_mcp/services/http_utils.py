from __future__ import annotations

import json
import uuid
from urllib import request


DEFAULT_TIMEOUT_SECONDS = 30.0


def _read_json_response(response) -> dict[str, object]:
    raw = response.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def get_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    req = request.Request(url, headers=headers or {}, method="GET")
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return _read_json_response(response)


def post_json(
    url: str,
    payload: dict[str, object],
    *,
    headers: dict[str, str] | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=req_headers,
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return _read_json_response(response)


def post_multipart(
    url: str,
    fields: dict[str, object],
    *,
    headers: dict[str, str] | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    boundary = f"----blender-mcp-{uuid.uuid4().hex}"
    lines: list[bytes] = []
    for key, value in fields.items():
        values = value if isinstance(value, (list, tuple)) else [value]
        for item in values:
            lines.append(f"--{boundary}".encode("utf-8"))
            if (
                isinstance(item, tuple)
                and len(item) == 3
                and isinstance(item[0], str)
                and isinstance(item[1], bytes)
                and isinstance(item[2], str)
            ):
                filename, content, content_type = item
                lines.append(
                    f'Content-Disposition: form-data; name="{key}"; filename="{filename}"'.encode("utf-8")
                )
                lines.append(f"Content-Type: {content_type}".encode("utf-8"))
                lines.append(b"")
                lines.append(content)
            else:
                lines.append(f'Content-Disposition: form-data; name="{key}"'.encode("utf-8"))
                lines.append(b"")
                if isinstance(item, bytes):
                    lines.append(item)
                else:
                    lines.append(str(item).encode("utf-8"))
    lines.append(f"--{boundary}--".encode("utf-8"))
    body = b"\r\n".join(lines) + b"\r\n"

    req_headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    if headers:
        req_headers.update(headers)
    req = request.Request(url, data=body, headers=req_headers, method="POST")
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return _read_json_response(response)
