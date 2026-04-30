# トラブルシュート

## 1. Codex App に `blender-official` が見えない

確認すること:

- installer が最後まで完了しているか
- Codex App を再起動したか
- Codex 設定に `mcp_servers.blender-official` が登録されているか
- installer のログに失敗がないか

まず Codex App を再起動してください。設定変更は再起動後に反映されます。

## 2. Blender の `MCP` add-on が有効にならない

確認すること:

- Blender 5.1 系を使っているか
- Blender の `Online Access` が有効か
- `Edit > Preferences > Get Extensions` に `MCP` が表示されるか
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

GUI を使わずログを採取する場合:

```powershell
uv run blender-mcp-installer --headless --output-dir <log-dir>
```

## 5. precision profile が分からない

precision profile は optional experimental 機能です。

通常の Blender MCP 導入だけを使う場合は、precision profile を導入しなくても構いません。高品質モデリング支援用の template、Skill、subagent template を試したい場合だけ有効にしてください。

config 追記予定を確認する場合:

```powershell
.\scripts\install_precision_profile.ps1 -PlanConfigMerge
```

precision profile 導入後に Codex App 側の挙動が不安定な場合は、`blender_precision` MCP server が残っていないか確認してください。v1 系では precision profile は template / Skill / subagent 配布に留め、standalone MCP server としては自動登録しません。

cleanup が行われた場合は、`config.toml.backup-<timestamp>` 形式のバックアップが作成されます。

## 6. Blender UI prompt が実行できない

確認すること:

- prompt 入力後に `Plan` を実行したか
- Preview の内容を確認したか
- `Confirm` を実行したか
- `Execute` 前にエラーが表示されていないか
- Codex CLI / Codex App / Blender MCP の接続前提が整っているか

この導線では、確認なしに変更を実行しない方針です。

## 7. 再導入したい

再導入前に `--plan` で変更予定を確認してください。

```powershell
uv run blender-mcp-installer --plan
```

Codex App の設定を変更した後は、Codex App を再起動してください。Blender 側の add-on 状態が不安定な場合は、Blender の再起動も行ってください。
