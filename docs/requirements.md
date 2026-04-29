# 要件定義

## 1. 背景

本プロジェクトは、Blender 公式の `blender_mcp` を前提に、Codex App と Codex CLI から Blender を扱えるようにすることを目的とする。

従来の独自 add-on / 独自 MCP server 構成は、更新追従と実運用の安定性に課題がある。今後は公式配布物と公式責務分離を優先し、このリポジトリは導入・統合・自動化・検証を担う。

## 2. 目的

- 公式 Blender MCP を Windows 環境へ導入できるようにする
- Codex App から公式 MCP server を経由して Blender を操作できるようにする
- Blender UI から Codex CLI を使った補助導線を用意する
- 公式更新に追従しやすい運用基盤を整える

## 3. 対象範囲

### 3.1 対象

- 公式 `blender_mcp` add-on / extension の導入支援
- 公式 `blender_mcp` server の利用前提整理
- Codex App からの公式 MCP 利用手順
- Blender UI から Codex CLI を呼ぶ補助導線
- 導入・更新・検証スクリプト
- 日本語ドキュメントと Issue 運用

### 3.2 非対象

- 公式 `blender_mcp` 自体の fork 前提改造
- 公式 add-on を全面的に置き換える独自 add-on 開発
- 公開ネットワーク前提の常設 server 構成
- 無制限の任意 Python 実行許可

## 4. MVP

### 4.1 MVP で満たすこと

- 公式 `mcp-1.0.0.zip` をローカルへ導入できる
- Blender 5.1 系で公式 add-on を有効化できる
- Codex App から公式 MCP を使う前提が docs で明確化されている
- Blender UI から Codex CLI を使う補助導線の設計方針が定義されている
- 公式構成への移行計画が Issue / docs に残っている

### 4.2 MVP 以降

- Codex App からの実運用コマンド群の拡張
- Blender UI からの補助操作実装
- 公式更新時の差分検知と更新自動化

## 5. 受け入れ条件

- 公式配布物の導入手順が再現可能である
- 公式構成を前提にした docs が日本語で整備されている
- 既存独自構成との差分と縮退方針が明確である
- GitHub Issue 上で判断経緯が追跡できる
