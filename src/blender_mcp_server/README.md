# Blender MCP Server Scaffold

`src/blender_mcp_server/` は `#5` の MCP サーバー最小スケルトンです。

含めているもの:

- エントリポイント
- サーバー生成プレースホルダー
- tool registry
- `blender_status` の最小経路
- service / transport 分離
- `/health`
- `/api/status`
- `/api/addon/status`

まだ含めていないもの:

- 公式 MCP Python SDK の tool 公開本体
- ログ、設定、AI アダプタ
