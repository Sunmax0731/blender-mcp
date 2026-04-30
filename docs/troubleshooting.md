# トラブルシュート

## 1. Codex App に `blender-official` が見えない

確認すること:

- installer が最後まで完了しているか
- Codex App を再起動したか
- Codex 設定に `mcp_servers.blender-official` が登録されているか
- installer のログに失敗がないか

設定変更は Codex App の再起動後に反映されます。

## 2. Blender の `MCP` add-on が有効にならない

確認すること:

- Blender 5.1 系を使っているか
- Blender の `Online Access` が有効か
- `Edit > Preferences > Get Extensions` または `Add-ons` に `MCP` が表示されるか
- installer の add-on 導入 step が成功しているか

公式 add-on はローカル TCP bridge server を使うため、`Online Access` が無効だと動作しない場合があります。

## 3. Codex App から Blender に接続できない

確認すること:

- Blender が起動しているか
- Blender の `MCP` add-on が有効か
- add-on の autostart が有効か
- host / port が add-on 側と MCP server 側で一致しているか
- セキュリティソフトがローカル接続を遮断していないか

Blender を起動した状態で、Codex App から screenshot 取得や状態取得を試してください。

## 4. installer が失敗する

確認すること:

- インターネット接続があるか
- Blender がインストール済みか
- PowerShell 実行が許可されているか
- installer のログに失敗 step が出ていないか

実行予定を確認する場合:

```powershell
uv run blender-mcp-installer --plan
```

GUI を使わずログを取得する場合:

```powershell
uv run blender-mcp-installer --headless --output-dir <log-dir>
```

## 5. precision profile が分からない

precision profile は optional experimental 機能です。

通常の Blender MCP 導入だけを使う場合、precision profile を導入しなくても構いません。高品質モデリング支援用の template、Skill、subagent template、`blender_precision` MCP server を試したい場合だけ有効にしてください。

導入すると、installer-managed venv に `blender-precision-mcp` package をインストールし、Codex App に `blender_precision` MCP server を登録します。`uvx` package として公開されている前提ではありません。

## 6. `blender_precision` が Codex App に表示されない

確認すること:

- precision profile のチェックを有効にして installer を実行したか
- installer ログで `precision-profile` step が成功しているか
- Codex App を再起動したか
- `%USERPROFILE%\.codex\config.toml` に `[mcp_servers.blender_precision]` があるか
- `%LOCALAPPDATA%\BlenderMcpInstaller\.precision-mcp-venv` または開発 repo の `.precision-mcp-venv` が存在するか

`config.toml` に過去の `uvx` 前提 section が残っている場合は、precision profile を再導入してください。installer がバックアップを作成したうえで現在の powershell 起動方式へ置き換えます。

## 7. `blender_precision` で `blender_unavailable` が返る

確認すること:

- まず `blender-official` で Blender 接続と screenshot 取得が成功しているか
- 実行している処理が dry-run ではなく `bpy` を必要とする live 処理か
- `model_spec` の確認だけでなく、scene 生成や review image 保存を sidecar 単独で実行しようとしていないか

`blender_unavailable` は、sidecar MCP server が `bpy` を直接保持していない実行コンテキストで live 処理を行ったときに返ります。これは precision profile 導入失敗とは限りません。`blender_precision` は dry-run と static validation に使い、live 処理は Blender background 実行または Blender 接続済み経路で実行してください。

## 8. live validation report や object list が採れない

確認すること:

- Blender を起動したうえで `blender-official` 接続確認が済んでいるか
- validation report、object list、review 画像を同じ artifact directory に保存する運用になっているか
- scene snapshot を公式 MCP から取得して sidecar validation に渡すか、Blender 側で report を生成する経路を選んでいるか

sidecar 単独で live validation が完結しない場合は、公式 MCP の scene snapshot を使うか、Blender background 実行で validation report と object list を生成してください。

## 9. 不要な補助 UI 登録を cleanup したい

過去の開発版で `blender_mcp` add-on の不要な Preferences 登録が残っている場合は、次を実行してください。

```powershell
.\scripts\remove_blender_prompt_ui.ps1
```

この script は公式 `MCP` add-on を残し、旧 `blender_mcp` の不要な Preferences 登録だけを削除します。実行後は Blender を再起動してください。
