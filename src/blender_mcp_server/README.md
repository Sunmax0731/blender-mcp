# Blender MCP Server Scaffold

`src/blender_mcp_server/` は `#5` の MCP サーバー最小スケルトンです。

含めているもの:

- エントリポイント
- サーバー生成プレースホルダー
- tool registry
- `blender_status` の最小経路
- service / transport 分離

まだ含めていないもの:

- 公式 MCP Python SDK への実接続
- ローカル HTTP transport の実装
- Blender 常時接続の受け口
- ログ、設定、AI アダプタ
