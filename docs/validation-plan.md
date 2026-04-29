# 検証計画

## 1. 目的

- 公式 Blender MCP を前提とした導入手順が再現できることを確認する
- Codex App / Codex CLI 連携の前提条件が崩れていないことを確認する
- docs と実装方針が一致していることを確認する

## 2. 検証レベル

### 2.1 静的確認

- docs の日本語表記確認
- 公式参照 URL の妥当性確認
- スクリプト引数、既定値、導入先の確認

### 2.2 導入確認

- 公式 `mcp-1.0.0.zip` が取得できる
- ローカル展開できる
- Blender add-on 配置先へ同期できる
- Blender 側で有効化対象として認識できる
- 公式 MCP server を `.official-mcp-venv` へ導入できる
- `blender-mcp --help` が実行できる
- Codex 設定へ `mcp_servers.blender-official` を追記できる

### 2.3 運用確認

- 公式構成を前提にした docs が読み替え不要で使える
- 導入・更新手順が PowerShell / コマンドプロンプトで実行できる
- 旧独自構成との混同が起きにくい

## 3. 証跡

- スクリプト実行ログ
- 展開済みファイル一覧
- Blender add-on 配置結果
- `.official-mcp-venv` の作成結果
- Codex 設定更新結果
- Issue コメント

## 4. 完了条件

- 公式 add-on 導入スクリプトが通る
- docs が公式前提に更新済みである
- Issue 上で移行方針と結果が追跡できる
