# blender-mcp v0.1.0

初回 Release です。
Windows 環境で、Blender 5.1 系と Codex App を前提に、公式 Blender MCP を 1 クリック導入しやすくするための配布物を公開します。

## 含まれるもの

- `blender-mcp-installer.exe`
  - Codex への `blender-official` MCP server 登録
  - Blender への公式 `mcp` extension 導入
  - 公式 `mcp` の有効化
  - 導入完了後の Blender 自動起動

## 前提条件

- Windows
- Blender 5.1 系がインストール済み
- Codex App がインストール済み
- ネットワーク接続があり、公式 Blender MCP 配布物を取得できる

## セットアップ

1. `blender-mcp-installer.exe` を実行する
2. 導入完了後に起動した Blender で `Edit > Preferences > Get Extensions` を開く
3. `MCP` が導入済みで、host=`localhost`、port=`9876`、autostart=`True` になっていることを確認する
4. Codex App を再起動する
5. Codex App から `blender-official` MCP server が見えていることを確認する

## 動作確認済み範囲

- 公式 `mcp-1.0.0.zip` の導入
- Blender 5.1 extension 管理経路 `user_default` への配置
- 公式 MCP server の専用仮想環境 `.official-mcp-venv` への導入
- Codex 設定への `mcp_servers.blender-official` 登録
- `bl_ext.user_default.mcp` の有効化
- `uv run pytest` `29 passed`
- `uv run blender-mcp-installer --plan` 成功
- Codex App からの live 接続確認
  - `get_screenshot_of_window_as_json`
  - `jump_to_tab_by_name("Modeling")`

## 既知制約

- Blender 本体と Codex App 本体の自動インストールは行いません
- macOS / Linux 向け配布は含みません
- 公式 Blender MCP 本体はこの Release で再配布せず、導入時に対応版 `v1.0.0` を取得します
- live 接続確認は Blender 起動状態に依存します

## 証跡

- 検証計画: [docs/validation-plan.md](validation-plan.md)
- リリース計画: [docs/release-plan.md](release-plan.md)
- テスト完了 milestone: [#15](https://github.com/Sunmax0731/blender-mcp/issues/15)
- Release 完了 milestone: [#16](https://github.com/Sunmax0731/blender-mcp/issues/16)
