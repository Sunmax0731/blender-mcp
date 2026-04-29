# Blender MCP Server

`src/blender_mcp_server/` は Blender 向けの MCP サーバー実装です。

## 構成

- `main.py`
  - `uvicorn` で ASGI アプリを起動します。
- `server.py`
  - `FastMCP` と `Starlette` を組み合わせて公開します。
- `tools/`
  - MCP から公開するツール定義です。
- `services/`
  - 状態管理、コマンドキュー、AI 連携、承認結果保持を扱います。
- `transport/`
  - Blender add-on 向けのローカル HTTP API を提供します。

## HTTP API

- `GET /health`
- `GET /api/status`
- `GET /api/tools`
- `GET /api/requests/{request_id}`
- `POST /api/ai/suggest`
- `POST /api/addon/status`
- `POST /api/addon/command/poll`
- `POST /api/addon/command-result`
- `POST /api/addon/approval-result`
- `POST /mcp`

## 公開ツール

- `blender_status`
- `blender_get_request_status`
- `blender_request_ai_suggestion`
- `blender_create_primitive`
- `blender_list_objects`
- `blender_transform_object`
- `blender_delete_object`

## AI 設定環境変数

- `BLENDER_MCP_OPENAI_API_KEY`
- `BLENDER_MCP_OPENAI_BASE_URL`
  - 既定値: `https://api.openai.com/v1`
- `BLENDER_MCP_OPENAI_MODEL`
  - 既定値: `gpt-4o-mini`
- `BLENDER_MCP_OPENAI_TIMEOUT_SECONDS`
  - 既定値: `30`

## ローカル起動

```powershell
uv run blender-mcp-server
```

`FastMCP` は `streamable-http` を `Starlette` に mount しており、Codex からは `/mcp` を通して利用します。
