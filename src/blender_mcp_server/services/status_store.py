from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import time


DEFAULT_STATUS = {
    "blenderRunning": False,
    "addonLoaded": False,
    "addonVersion": None,
    "blenderVersion": None,
    "transportStatus": "disconnected",
    "lastSeenEpoch": None,
}

_state = deepcopy(DEFAULT_STATUS)
_lock = Lock()


def reset_status_state() -> dict[str, object]:
    with _lock:
        _state.clear()
        _state.update(deepcopy(DEFAULT_STATUS))
        return deepcopy(_state)


def get_status_state() -> dict[str, object]:
    with _lock:
        return deepcopy(_state)


def update_status_state(payload: dict[str, object]) -> dict[str, object]:
    with _lock:
        _state["blenderRunning"] = bool(payload.get("blenderRunning", True))
        _state["addonLoaded"] = bool(payload.get("addonLoaded", True))
        _state["addonVersion"] = payload.get("addonVersion")
        _state["blenderVersion"] = payload.get("blenderVersion")
        _state["transportStatus"] = payload.get("transportStatus", "connected")
        _state["lastSeenEpoch"] = time()
        return deepcopy(_state)
