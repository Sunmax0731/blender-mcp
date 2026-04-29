from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime
from datetime import timezone
from threading import Condition


_condition = Condition()
_approval_results: dict[str, dict[str, object]] = {}


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def reset_approval_state() -> None:
    with _condition:
        _approval_results.clear()
        _condition.notify_all()


def submit_approval_result(result: Mapping[str, object]) -> dict[str, object]:
    request_id = result.get("requestId")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("requestId is required.")

    normalized = deepcopy(dict(result))
    normalized.setdefault("timestamp", _utc_timestamp())

    with _condition:
        _approval_results[request_id] = normalized
        _condition.notify_all()

    return normalized


def get_approval_result(request_id: str) -> dict[str, object] | None:
    with _condition:
        result = _approval_results.get(request_id)
        if result is None:
            return None
        return deepcopy(result)
