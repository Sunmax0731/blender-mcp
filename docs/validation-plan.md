# 検証計画

## 1. 目的

- 公式 Blender MCP を前提とした導入手順が再現できることを確認する
- 1 クリック導入アプリから主要導入ステップを一括実行できることを確認する
- Codex App / Codex CLI 連携の前提条件が崩れていないことを確認する
- docs と実装方針が一致していることを確認する

## 2. 検証レベル

### 2.1 静的確認

- docs の日本語表記確認
- 公式参照 URL の妥当性確認
- スクリプト引数、既定値、導入先の確認
- 1 クリック導入アプリの実行ステップと docs の一致確認

### 2.2 導入確認

- 公式 `mcp-1.0.0.zip` が取得できる
- ローカル展開できる
- Blender extension 管理経路へ導入できる
- Blender の `Get Extensions` で `MCP` が認識される
- 公式 `mcp` が有効化される
- 公式 MCP server を `.official-mcp-venv` へ導入できる
- `blender-mcp --help` が実行できる
- Codex 設定へ `mcp_servers.blender-official` を追記できる
- `blender-mcp-installer --plan` で実行予定ステップを確認できる
- 1 クリック導入アプリから各 PowerShell ステップを順番に呼び出せる

### 2.3 live 接続確認

- Blender 起動後に Codex App から公式 MCP tool を呼び出せる
- `get_screenshot_of_window_as_json` が成功する
- `jump_to_tab_by_name` によりワークスペース切替が成功する

### 2.4 運用確認

- 公式構成を前提にした docs が読み替え不要で使える
- 導入・更新手順が PowerShell / コマンドプロンプトで実行できる
- 利用者向け導線が公式 `mcp` 前提として読める
- `start_official_blender_mcp.ps1` から Blender 実行パスを解決できる
- Codex App から Blender ワークスペース切替や状態取得が実行できる
- 1 クリック導入アプリのログから失敗箇所を追跡できる

### 2.5 Blender UI プロンプト導線確認

- プロンプト入力、実行計画作成、Preview、Confirm、Execute の状態遷移が docs と一致している
- 危険操作を含む計画は明示承認なしに実行できない
- Codex CLI 未検出時、公式 MCP 未接続時、実行計画不備時のエラーが利用者に表示される
- 実行結果とログが確認できる

## 3. 証跡

- スクリプト実行ログ
- `blender-mcp-installer` 実行ログ
- 展開済みファイル一覧
- Blender add-on 配置結果
- 公式 `mcp` 有効化ログ
- `.official-mcp-venv` の作成結果
- Codex 設定更新結果
- Codex App からの接続結果
- Blender UI プロンプト導線の Preview / Confirm / Execute 確認結果
- Issue コメント

## 4. 完了条件

- 公式 add-on 導入スクリプトが通る
- 1 クリック導入アプリ経由でも主要導入が追跡できる
- docs が公式前提に更新済みである
- Issue 上で移行方針と結果が追跡できる
