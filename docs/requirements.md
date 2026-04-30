# 要件定義

## 1. 背景

本プロジェクトは、Blender 公式の `blender_mcp` を前提に、Codex App と Codex CLI から Blender を扱えるようにすることを目的とする。

従来の独自 add-on / 独自 MCP server 構成は、更新追従と実運用の安定性に課題がある。今後は公式配布物と公式責務分離を優先し、このリポジトリは導入・統合・自動化・検証を担う。

## 2. 目的

- 公式 Blender MCP を Windows 環境へ導入できるようにする
- Codex App から公式 MCP server を経由して Blender を操作できるようにする
- v1 系では Blender UI の独自 Prompt 導線を利用者向け導線から外し、公式 MCP 導線に一本化する
- 公式更新に追従しやすい運用基盤を整える
- Release 成果物として、1 クリックで導入を進められる Windows 向けアプリを提供する

## 3. 対象範囲

### 3.1 対象

- 公式 `blender_mcp` add-on / extension の導入支援
- 公式 `blender_mcp` server の利用前提整理
- Codex App からの公式 MCP 利用手順
- 既存環境に残った旧補助 Prompt UI 登録の cleanup
- 導入・更新・検証スクリプト
- 1 クリック導入アプリ
- 日本語ドキュメントと Issue 運用

### 3.2 非対象

- 公式 `blender_mcp` 自体の fork 前提改造
- 公式 add-on を全面的に置き換える独自 add-on 開発
- Blender N メニューに表示する独自 Prompt UI の v1 利用者向け提供
- 公開ネットワーク前提の常設 server 構成
- 無制限の任意 Python 実行許可
- macOS / Linux 向け配布物の同時対応
- Blender 本体や Codex App 本体の自動インストール

## 4. 1クリック導入アプリ要件

### 4.1 成果物

- Windows ローカル環境で起動する GUI アプリを提供する
- 利用者は原則 1 回の起動操作で導入フローを開始できる
- 配布形態は Python 製 GUI ラッパーを `exe` 化したものを初期方針とする

### 4.2 アプリが実行する範囲

- 公式 add-on 配布物を取得し、Blender add-on 配置先へ導入する
- 公式 MCP server を専用仮想環境へ導入する
- `%USERPROFILE%\.codex\config.toml` 相当の Codex 設定へ `mcp_servers.blender-official` を追記する
- Blender 側で公式 `mcp` add-on を有効化する
- 導入後の確認項目とログ保存先を利用者へ提示する

### 4.3 アプリが満たすべき性質

- 既存 PowerShell スクリプト資産を可能な限り内部利用する
- 失敗したステップを利用者が識別できる
- 再実行時に致命的な競合を起こしにくい
- ローカル完結を前提とし、外部公開前提の常駐サービスを増やさない

### 4.4 前提条件

- 利用者の PC に Blender 5.1 系が導入済みである
- 利用者の PC に Codex App が導入済みである
- ネットワーク接続により公式配布物を取得できる
- ローカル設定変更を許可できる Windows 環境である

## 5. MVP

### 5.1 MVP で満たすこと

- 公式 `mcp-1.0.0.zip` をローカルへ導入できる
- Blender 5.1 系で公式 add-on を有効化できる
- Codex App から公式 MCP を使う前提が docs で明確化されている
- 旧補助 Prompt UI が利用者向け導線に残らない
- 公式構成への移行計画が Issue / docs に残っている
- 1 クリック導入アプリの要件、対象、非対象、配布方針が明確化されている

### 5.2 MVP 以降

- Codex App からの実運用コマンド群の拡張
- Blender UI 補助操作は v2 以降の再検討対象として扱う
- 公式更新時の差分検知と更新自動化
- 1 クリック導入アプリの GUI 実装と `exe` 配布
- 導入後の live 接続確認自動化

## 6. Blender UI 補助導線の扱い

v1 系では、Blender UI から prompt を入力する独自補助導線は利用者向け機能に含めない。

### 6.1 対象

- 公式 `MCP` add-on の Preferences による host / port / autostart 確認
- 旧 `blender_mcp` add-on の Preferences 登録 cleanup
- Codex App から公式 MCP を使う利用手順の明確化

### 6.2 非対象

- Blender Sidebar に独自 Prompt panel を表示すること
- Codex CLI を Blender UI から直接呼び出すこと
- 確認なしの任意 Python 実行
- ユーザー確認を省略したシーン破壊操作

### 6.3 将来検討

Blender UI 補助導線を再開する場合は、公式 add-on と利用者導線を混同させない名称、表示位置、接続状態、preview / confirm / execute の安全設計を Issue で再定義してから実装する。

## 7. 受け入れ条件

- 公式配布物の導入手順が再現可能である
- 公式構成を前提にした docs が日本語で整備されている
- 既存独自構成との差分と縮退方針が明確である
- GitHub Issue 上で判断経緯が追跡できる
- 1 クリック導入アプリの成果物定義と適用範囲が追跡できる
- Blender UI 補助導線を v1 利用者向け対象外にする判断が追跡できる

## 8. v2 精密モデリング要件

v2 では、公式 Blender MCP を土台に、より高品質なモデル制作、検証、視覚レビュー、Blender add-on 活用を行うための sidecar MCP server と配布用テンプレートを追加対象とする。

### 8.1 対象

- Codex から呼び出す高水準 tool 群を提供する `blender-precision-mcp` sidecar / proxy
- profile / config / tool pack に応じた MCP tool 公開制御
- `model_spec.yaml` による制作意図、寸法、構成要素、材質、検証条件の明文化
- `validation_report` によるシーン検証、メッシュ検証、材質検証、視覚レビュー証跡
- `addon_registry` による承認済み Blender add-on、operator、property map、検証基準の管理
- Codex 向け `AGENTS.md` / `SKILL.md` / subagent template の配布
- 利用者が導入できる precision profile / Skill / template の installer 連携

### 8.2 非対象

- Codex MCP 設定の `args` で tool を直接注入する設計
- 未承認 add-on operator の実行
- UI 操作や modal operator 前提の自動化
- 確認なしの破壊的シーン編集
- 任意 Python / `bpy` 実行を利用者向け通常導線で許可すること

### 8.3 安全要件

- `command` / `args` は MCP server 起動のために使い、公開 tool は server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で制御する
- `args` で渡すのは profile、config、tool pack などの server 起動設定に限定する
- 破壊的操作はバックアップ作成と `preview -> confirm -> execute` を必須にする
- add-on 利用は承認済み registry、operator poll、context 準備、dry-run 可能性を確認してから実行する
- `bpy.ops` / `bpy.context` / operator context override は add-on integration の設計領域として分離する
