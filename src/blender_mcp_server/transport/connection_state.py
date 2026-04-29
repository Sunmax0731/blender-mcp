def get_connection_state() -> dict[str, object]:
    return {
        "blenderRunning": False,
        "addonLoaded": False,
        "transportStatus": "disconnected",
    }
