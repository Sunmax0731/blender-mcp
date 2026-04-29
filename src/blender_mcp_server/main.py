from __future__ import annotations

import uvicorn

from .server import create_server


def main():
    server = create_server()
    print(f"Blender MCP server listening on http://{server.host}:{server.port}")
    uvicorn.run(server.app, host=server.host, port=server.port, log_level="info")


if __name__ == "__main__":
    main()
