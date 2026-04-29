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

- 2026-04-30 時点の安定版: `v1.0.0`

## 3. 本リポジトリが提供するもの

### 3.1 導入スクリプト

- 公式 `mcp-1.0.0.zip` を取得する
- ローカル展開して Blender add-on 配置先へ同期する
- 将来的にバージョン指定更新へ対応できる構造にする
- 公式 MCP server は専用仮想環境 `D:\Claude\MCP\.official-mcp-venv` へ導入する
- Codex App 用の MCP 設定登録スクリプトを提供する

### 3.1.1 Blender 側の前提

- `Edit > Preferences > Add-ons` で `MCP` を有効化する
- legacy `blender_mcp` add-on が有効なら無効化する
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

## 4. 独自構成の扱い

- 既存独自 add-on / server は移行中資産とする
- 新規主経路としては扱わない
- 公式移行が完了するまで、比較・参考・退避対象として保持する

## 5. 検証観点

- 公式配布物が取得できること
- Blender へ導入できること
- Blender 側で add-on が有効化できること
- legacy add-on と競合せず公式 `mcp` が主経路になること
- 公式 MCP server が専用仮想環境へ導入できること
- Codex 設定へ `mcp_servers.blender-official` を登録できること
- 公式構成を前提に docs が一致していること
- 補助導線が公式構成を壊さないこと
