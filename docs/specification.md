# 仕様

## 1. 前提

- 対象 Blender: 5.1 系
- 公式 Blender MCP: `v1.0.0` を初期基準とする
- OS: Windows
- Python 環境: 3.11 系
- パッケージ管理: `uv`

## 2. 公式配布物

### 2.1 add-on / extension 配布物

- リリース資産: `mcp-1.0.0.zip`
- 配置対象: Blender add-on / extension
- 確認済み主要ファイル:
  - `blender_manifest.toml`
  - `__init__.py`
  - `cli.py`
  - `mcp_to_blender_server.py`

### 2.2 リリース版数

- 2026-04-30 時点で確認した初期対応版: `v1.0.0`

## 3. 本リポジトリが提供するもの

### 3.1 導入スクリプト

- 公式 `mcp-1.0.0.zip` を取得する
- ローカル展開して Blender add-on 配置先へ同期する
- 将来的にバージョン指定更新へ対応できる構造にする
- 公式 MCP server はリポジトリルート直下の専用仮想環境 `.official-mcp-venv/` へ導入する
- Codex App 用の MCP 設定登録スクリプトを提供する

### 3.1.1 Blender 側の前提

- `Edit > Preferences > Get Extensions` で `MCP` を確認し有効化する
- Blender の `Online Access` を有効化する
- host / port / autostart は add-on 設定に従う
- 背景実行では `--online-mode` が必要になる
- Blender 実行パスは `BLENDER_PATH` で明示できるが、Codex 起動スクリプト側でも自動解決する

### 3.2 ドキュメント

- 公式構成の説明
- Codex App からの利用前提
- Blender UI から Codex CLI を使う補助導線
- 更新と検証の運用手順

### 3.3 補助機能

- 公式 add-on に干渉しない補助 UI / 補助スクリプト
- 公式構成で不足する運用自動化

### 3.4 1クリック導入アプリ

- 単一の GUI エントリポイントから導入フローを開始できる
- 内部では既存 PowerShell スクリプトを順次呼び出す
- 実行結果、失敗箇所、再実行可否を UI 上で利用者へ示す

## 4. 1クリック導入アプリ仕様

### 4.1 起動前確認

- Blender 実行ファイルの探索
- Codex 設定ファイルの存在確認
- add-on 配置先の解決
- ネットワーク接続前提の注意表示

### 4.2 実行ステップ

1. 公式 add-on 配布物を取得する
2. Blender add-on 配置先へ導入する
3. 公式 MCP server を専用仮想環境へ導入する
4. Codex 設定へ `mcp_servers.blender-official` を登録する
5. Blender 側で公式 `mcp` を有効化する
6. 導入後の確認項目を表示する

### 4.3 UI 要素

- 実行開始ボタン
- 現在ステップの進捗表示
- 実行ログ表示領域
- 完了後の確認項目表示
- 失敗時の再実行案内

### 4.4 ログと証跡

- 実行ログをローカルファイルへ保存する
- UI 上でも直近ログを参照できる
- 失敗したステップ名と例外メッセージを保持する
- 再実行時に前回ログを消さず追記または別名保存する

### 4.5 確認フロー

- 既存 Codex 設定の変更前に、変更対象ファイルとバックアップ作成を利用者へ示す
- Blender 側の設定変更前に、何を切り替えるかを利用者へ示す
- 危険操作は `preview -> confirm -> execute` を守る

## 5. 独自構成の扱い

- 既存独自 add-on / server は移行中資産とする
- 新規主経路としては扱わない
- 公式移行が完了するまで、比較・参考・退避対象として保持する

## 6. 検証観点

- 公式配布物が取得できること
- Blender へ導入できること
- Blender 側で add-on が有効化できること
- 公式 `mcp` が主経路として有効化されること
- 公式 MCP server が専用仮想環境へ導入できること
- Codex 設定へ `mcp_servers.blender-official` を登録できること
- 公式構成を前提に docs が一致していること
- 補助導線が公式構成を壊さないこと
- GUI 導入アプリから実行順序とログが追跡できること
