# Blender MCP Server

`src/blender_mcp_server/` は Blender 向け MCP サーバー実装です。

## 構成

- `main.py`
  - `uvicorn` で ASGI アプリを起動します。
- `server.py`
  - `FastMCP` と `Starlette` を組み合わせて公開します。
- `tools/`
  - MCP から公開するツール定義です。
- `services/`
  - 状態管理、コマンドキュー、承認結果保持、Codex CLI 連携を扱います。
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

## AI 提案経路

このリポジトリでは 2 つの経路を使い分けます。

- Codex App からの Blender 操作
  - MCP ツール経由で `blender-mcp-server` を利用します。
- Blender UI からのプロンプト送信
  - `Codex CLI` をバックグラウンド実行して提案文を生成します。

`/api/ai/suggest` は外部 OpenAI 互換 API ではなく、ローカル `Codex CLI` を使います。

## Codex CLI 設定環境変数

- `BLENDER_MCP_CODEX_COMMAND`
  - 既定値: Windows は `codex.cmd`、それ以外は `codex`
- `BLENDER_MCP_CODEX_MODEL`
  - 任意。指定時だけ `--model` を付けます。
- `BLENDER_MCP_CODEX_TIMEOUT_SECONDS`
  - 既定値: `45`
- `BLENDER_MCP_CODEX_WORKDIR`
  - 既定値: OS の一時ディレクトリ

## ローカル起動

```powershell
uv run blender-mcp-server
```

`FastMCP` は `streamable-http` を `Starlette` に mount しており、Codex App からは `/mcp` を通して利用します。
