# トラブルシュート

## 1. Codex App に `blender-official` が見えない

確認すること:

- installer が最後まで完了しているか
- Codex App を再起動したか
- `%USERPROFILE%\\.codex\\config.toml` に `blender-official` があるか
- installer のログに失敗 step がないか

## 2. Blender の `MCP` add-on が有効にならない

確認すること:

- Blender 5.1 系を使っているか
- `Online Access` が有効か
- `Get Extensions` または `Add-ons` に `MCP` が表示されるか
- installer の `official-addon` と `enable-addon` が成功しているか

## 3. Blender MCP パネルが出ない

確認すること:

- installer の `supplemental-addon` step が成功しているか
- `Add-ons > Blender MCP` が有効か
- Blender を再起動したか

補助 add-on だけ再導入したい場合:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_supplemental_blender_addon.ps1
```

## 4. External Services が空のまま

確認すること:

- `Add-ons > Blender MCP > External Services` で対象サービスを有効化したか
- 3D View の `Blender MCP > 外部サービス > Preferences 読み込み` を押したか
- `mode` が正しく設定されているか

## 5. `plugin_bridge add-on未検出` が出る

確認すること:

- 対象 plugin が Blender に導入済みか
- 対象 plugin が有効か
- installer で第三者 plugin のチェックを有効にしたか

2026年5月1日時点で手動確認済みの正常表示:

- Meshy: `plugin_bridge ready (Meshy official plugin)`
- Tripo AI: `plugin_bridge ready (Tripo 3D)`
- Hyper3D Rodin: `plugin_bridge ready (RodinBridge)`

## 6. Rodin の黒いコンソールが出る

RodinBridge add-on 側の debug 出力です。今回の Release では既知のノイズとして扱っています。

## 7. installer が失敗する

確認すること:

- インターネット接続があるか
- Blender がインストール済みか
- PowerShell 実行が許可されているか
- ログに失敗 step が出ていないか

実行予定だけ確認する場合:

```powershell
uv run blender-mcp-installer --plan
```

GUI を使わずログを取得する場合:

```powershell
uv run blender-mcp-installer --headless --output-dir <log-dir>
```

## 8. precision profile が分からない

precision profile は optional experimental 機能です。

通常の公式 Blender MCP 導入だけを使う場合は不要です。高品質モデリング支援や `blender_precision` を試したい場合だけ有効にしてください。

## 9. `blender_precision` が表示されない

確認すること:

- precision profile のチェックを有効にしたか
- installer の `precision-profile` step が成功しているか
- Codex App を再起動したか

## 10. `blender_precision` で `blender_unavailable` が返る

確認すること:

- まず `blender-official` で接続確認できているか
- 実行している処理が dry-run ではなく live 処理か

これは precision profile 導入失敗とは限りません。sidecar に `bpy` がない実行コンテキストで live 処理を呼んだ場合に返ります。

## 11. External Services の API 実行が失敗する

確認すること:

- API キーが正しいか
- endpoint を誤っていないか
- `cloud_api` と `plugin_bridge` の mode を取り違えていないか
- 追加 JSON が provider の想定形式か

`v1.2.0` では API キー未入手のため、実サービス成功までは Release 条件に含めていません。
