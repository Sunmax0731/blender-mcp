from .server import create_server


def main():
    server = create_server()
    print(f"Blender MCP server scaffold ready: {server.name}")


if __name__ == "__main__":
    main()
