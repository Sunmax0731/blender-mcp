from .server import create_server


def main():
    server = create_server()
    print(f"Blender MCP server listening on http://{server.host}:{server.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
