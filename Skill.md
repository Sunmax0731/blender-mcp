# Skill

`blender-mcp` を進めるうえで必要なスキルと実行方針をまとめる。

## 1. 必要スキル

### 1.1 公式 Blender MCP 調査

- 公式紹介ページ、公式リポジトリ、公式リリースを読み、構成と責務分離を把握する
- add-on 配布物と server 実装の違いを切り分ける
- 公式更新に追従しやすい差分設計を行う

### 1.2 Blender add-on 運用

- Blender add-on / extension の配置、再読み込み、設定確認
- `bpy` による最小限の補助 UI 実装
- 公式 add-on と競合しない追加機能設計

### 1.3 MCP server 運用

- MCP クライアント/サーバーの役割理解
- Codex App から公式 MCP server を呼ぶ構成設計
- ローカルプロセスの起動、監視、ログ確認

### 1.4 Codex CLI 連携

- `codex exec` の非対話実行
- タイムアウト、失敗時のフォールバック設計
- Blender UI からの自然言語導線設計

### 1.5 テストと自動化

- `pytest`
- Blender 実機確認
- add-on 更新、server 起動、スクリーンショット取得の自動化

## 2. 実行方針

- まず公式構成へ寄せる
- 公式で足りない部分だけ独自実装する
- 人向け文書は日本語で整備する
- 変更理由と判断は Issue に残す

## 3. 現在の主対象

- 公式 `blender_mcp` の導入支援
- Codex App からの公式 MCP 利用
- Blender UI から Codex CLI へつなぐ補助導線
- 既存独自構成から公式構成への移行計画
