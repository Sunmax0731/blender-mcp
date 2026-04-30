# blender-mcp v1.0.2

`v1.0.2` は、precision profile の Codex MCP 設定を安全側へ修正する hotfix Release です。

## 修正内容

- v1 系では `blender_precision` MCP server を自動登録しない方針に変更しました。
- `blender-precision-mcp` は experimental scaffold であり、standalone `uvx` package として配布していないためです。
- 過去の installer で生成された experimental な `[mcp_servers.blender_precision]` section がある場合は、`config.toml` をバックアップしたうえで削除します。
- precision profile は引き続き template、Skill、subagent template として導入されます。

## 期待される Codex App 表示

v1.0.2 適用後、Codex App の MCP サーバー一覧には通常次が表示されます。

- `blender-official`
- 既存利用中の他 MCP server

`blender_precision` は v1 系では表示されない状態が意図した動作です。

## 検証

- `uv run pytest`: 58 passed
- `uvx blender-precision-mcp --help`: package registry に存在しないことを確認
- generated `[mcp_servers.blender_precision]` section の cleanup を一時 config で確認
- packaged installer で precision profile step の cleanup script が展開されることを確認

## GitHub Release に添付するもの

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v1.0.2.json`
