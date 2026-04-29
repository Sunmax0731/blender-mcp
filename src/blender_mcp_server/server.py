from .tools.registry import build_tool_registry


class ServerScaffold:
    def __init__(self, name: str, tool_registry: dict[str, object]):
        self.name = name
        self.tool_registry = tool_registry


def create_server() -> ServerScaffold:
    return ServerScaffold(
        name="blender-mcp-server",
        tool_registry=build_tool_registry(),
    )
