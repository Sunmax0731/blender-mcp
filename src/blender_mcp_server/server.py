from .transport.http_app import create_http_server
from .tools.registry import build_tool_registry


class ServerScaffold:
    def __init__(self, name: str, host: str, port: int, tool_registry: dict[str, object], http_server):
        self.name = name
        self.host = host
        self.port = port
        self.tool_registry = tool_registry
        self.http_server = http_server

    def serve_forever(self):
        self.http_server.serve_forever()


def create_server() -> ServerScaffold:
    host = "127.0.0.1"
    port = 8765
    http_server = create_http_server(host=host, port=port)
    return ServerScaffold(
        name="blender-mcp-server",
        host=host,
        port=port,
        tool_registry=build_tool_registry(),
        http_server=http_server,
    )
