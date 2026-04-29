from ..transport.connection_state import get_connection_state


def build_status_payload() -> dict[str, object]:
    state = get_connection_state()
    return {
        "success": True,
        "data": state,
    }
