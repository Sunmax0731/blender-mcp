# blender-mcp v1.0.3

`v1.0.3` は、v1 系の利用者向け導線を公式 Blender MCP に一本化する hotfix Release です。

## 修正内容

- installer に `remove-prompt-ui` step を追加しました
- 過去の開発版で Blender Preferences に残った旧 `blender_mcp` add-on 登録を削除します
- 公式 `MCP` add-on、`bl_ext.user_default.mcp`、公式 extension directory は削除しません
- v1 利用者向け docs を `Codex App -> 公式 Blender MCP server -> 公式 Blender add-on -> Blender` の導線に揃えました

## 期待される状態

installer 実行後、Codex App の MCP server 一覧には通常 `blender-official` が表示されます。

Blender 側では Preferences の公式 `MCP` add-on を確認し、自然言語での制作指示は Codex App から行います。

## 検証

- `uv run pytest`: 58 passed
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender`
- `.\dist\one-click-installer\blender-mcp-installer.exe --plan --include-precision-profile --no-launch-blender`
- `.\dist\one-click-installer\blender-mcp-installer.exe --headless --include-precision-profile --no-launch-blender`
- `.\scripts\remove_blender_prompt_ui.ps1`
  - `PROMPT_UI_REMOVED_PREFS=['blender_mcp']`
  - `OFFICIAL_MCP_STATES={'mcp': (False, False), 'bl_ext.user_default.mcp': (True, True)}`

## GitHub Release に添付するもの

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v1.0.3.json`
