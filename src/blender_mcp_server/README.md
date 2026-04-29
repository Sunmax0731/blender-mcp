# Blender MCP Server

`src/blender_mcp_server/` は `#5` `#6` のサーバー実装を置くディレクトリです。

現在の構成:

- `main.py`
  - `uvicorn` で ASGI アプリを起動
- `server.py`
  - `FastMCP` と `Starlette` を組み立てる
- `tools/`
  - MCP 公開ツール定義
- `services/`
  - 状態管理、コマンドキュー、実行待機
- `transport/`
  - add-on 向け HTTP API

現在の公開面:

- `GET /health`
- `GET /api/status`
- `GET /api/tools`
- `POST /api/addon/status`
- `POST /api/addon/command/poll`
- `POST /api/addon/command-result`
- `POST /mcp`

MCP 側で公開している最小ツール:

- `blender_status`
- `blender_create_primitive`
- `blender_list_objects`
- `blender_delete_object`

ローカル起動例:

```powershell
uv run blender-mcp-server
```

`FastMCP` は `streamable-http` を `Starlette` に mount しており、Codex 側は `/mcp` を接続先として使用します。
