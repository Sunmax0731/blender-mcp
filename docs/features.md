# 機能説明

## 1. 1クリック導入アプリ

Windows 向けに、公式 Blender MCP の導入をまとめて実行する GUI アプリです。

主な機能:

- 公式 Blender MCP add-on の導入
- 公式 Blender MCP server の導入
- Codex App の `blender-official` MCP server 登録
- Blender 側の公式 `mcp` add-on 有効化
- 導入ログ表示
- 導入完了後の `Finish` 操作

## 2. plan mode

実際に変更する前に、installer が実行する予定の step を表示します。

```powershell
uv run blender-mcp-installer --plan
```

導入前の確認、再導入前の確認、トラブルシュートに使います。

## 3. headless mode

GUI を使わずに installer step を実行します。

```powershell
uv run blender-mcp-installer --headless
```

ログ採取や検証環境での再現確認に使います。

## 4. Codex App 連携

Codex App に `blender-official` MCP server を登録します。

登録後は Codex App を再起動し、Blender を起動した状態で Blender MCP tool を使います。

## 5. Blender UI prompt 補助導線

Blender UI から prompt を入力し、`Plan -> Confirm -> Execute` の流れで Blender scene に変更を反映するための補助導線です。

公式 Blender MCP を置き換えるものではなく、利用者の確認と承認を扱う補助レイヤーです。

## 6. precision profile

高品質モデリング支援のための optional experimental 機能です。

含まれるもの:

- precision template / schema
- `blender-precision-mcp` sidecar scaffold
- `model_spec`
- `validation_report`
- `addon_registry`
- visual QA manifest
- Skill / AGENTS / subagent template

v1.0.0 では experimental として同梱します。正式な完成機能ではありません。

## 7. 安全方針

- 公式 Blender MCP を中核にする
- 危険操作は `preview -> confirm -> execute` を守る
- 任意 Python / `bpy` 実行を通常導線では許可しない
- 既存 Codex 設定を変更する場合は、バックアップと確認を前提にする
- 外部公開前提の常駐 server 構成にしない
