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

### 1.6 GitHub Issue 運用

- `gh issue create` / `gh issue comment` に日本語本文を渡すときの PowerShell 文字コード差異を理解する
- 標準入力パイプではなく UTF-8 without BOM のファイル経由で本文を渡す
- 投稿後は GitHub 上で本文が文字化けしていないか確認する

## 2. 実行方針

- まず公式構成へ寄せる
- 公式で足りない部分だけ独自実装する
- 人向け文書は日本語で整備する
- 変更理由と判断は Issue に残す
- ユーザー判断が必要な Issue は、候補案を並べるだけでなく、判断材料と推奨案まで含めて作る

## 2.2 GitHub 投稿の再発防止

- PowerShell では `[Console]::OutputEncoding` が UTF-8 でも `$OutputEncoding` が `US-ASCII` のままなことがある
- `gh ... --body-file -` に日本語本文をパイプすると、Windows code page 932 と組み合わさって文字化けすることがある
- Issue 本文、Issue コメント、PR コメントの日本語本文は、一時 UTF-8 without BOM ファイルを作って `--body-file` に渡す
- 投稿後は `gh issue view` か GitHub 画面で本文確認まで行って完了とする

## 2.1 判断提案スキル

- 判断が必要なときは、Issue に候補 3 案を基本として提示する
- 各案には長所、短所、影響範囲、前提条件を書く
- 判断材料として、既存実装との整合、公式方針との一致、実装量、保守性、検証コストを整理する
- 最後に推奨案を 1 つ選び、その理由を短く明確に書く

## 3. 現在の主対象

- 公式 `blender_mcp` の導入支援
- Codex App からの公式 MCP 利用
- Blender UI から Codex CLI へつなぐ補助導線
- 既存独自構成から公式構成への移行計画

## 4. 配布用 Skill

利用者が Codex 環境へ導入して使う Skill は、repo 直下の `skills/` に配置する。

- `skills/blender-quality-modeling/`: Blender MCP で高品質なモデル、マテリアル、ライト、カメラ、検証証跡を作るための Skill
- `skills/blender-addon-development/`: Blender アドオン / extension の設計、実装、検証、配布を支援する Skill

配布とインストール手順は [docs/skills.md](docs/skills.md) にまとめる。
