from .status_store import get_status_state


def build_status_payload() -> dict[str, object]:
    state = get_status_state()
    return {
        "success": True,
        "data": state,
    }
