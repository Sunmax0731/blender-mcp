from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime
from datetime import timezone
from threading import Condition
from time import monotonic


_condition = Condition()
_pending_commands: deque[dict[str, object]] = deque()
_results: dict[str, dict[str, object]] = {}
_sequence = 0


def _next_request_id() -> str:
    global _sequence
    _sequence += 1
    return f"req-{_sequence:05d}"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_command_envelope(
    *,
    action: str,
    params: Mapping[str, object] | None = None,
    requires_confirmation: bool = False,
) -> dict[str, object]:
    return {
        "requestId": _next_request_id(),
        "timestamp": _utc_timestamp(),
        "action": action,
        "params": dict(params or {}),
        "requiresConfirmation": requires_confirmation,
    }


def reset_command_state() -> None:
    global _sequence
    with _condition:
        _pending_commands.clear()
        _results.clear()
        _sequence = 0
        _condition.notify_all()


def enqueue_command(
    *,
    action: str,
    params: Mapping[str, object] | None = None,
    requires_confirmation: bool = False,
) -> dict[str, object]:
    command = create_command_envelope(
        action=action,
        params=params,
        requires_confirmation=requires_confirmation,
    )
    with _condition:
        _pending_commands.append(deepcopy(command))
        _condition.notify_all()
    return command


def claim_next_command() -> dict[str, object] | None:
    with _condition:
        if not _pending_commands:
            return None
        return deepcopy(_pending_commands.popleft())


def submit_command_result(result: Mapping[str, object]) -> dict[str, object]:
    request_id = result.get("requestId")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("requestId is required.")

    normalized = deepcopy(dict(result))
    normalized.setdefault("timestamp", _utc_timestamp())
    normalized.setdefault("success", False)

    with _condition:
        _results[request_id] = normalized
        _condition.notify_all()
    return normalized


def wait_for_command_result(request_id: str, timeout_seconds: float) -> dict[str, object] | None:
    deadline = monotonic() + timeout_seconds
    with _condition:
        while request_id not in _results:
            remaining = deadline - monotonic()
            if remaining <= 0:
                return None
            _condition.wait(timeout=remaining)

        return deepcopy(_results.pop(request_id))
