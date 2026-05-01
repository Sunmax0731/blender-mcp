# 機能説明

## 1. 1クリック導入アプリ

Windows 向けに、公式 Blender MCP の導入をまとめて実行する GUI アプリです。

主な機能:

- 公式 Blender MCP add-on の導入
- 公式 Blender MCP server の専用 venv への導入
- Codex App の `blender-official` 登録
- Blender 側の公式 `mcp` add-on 有効化
- 旧補助 UI 登録の cleanup
- Meshy / Tripo / Rodin plugin の自動導入
- 補助 Blender add-on の自動導入
- 導入ログ表示
- 導入完了後の Blender 起動

## 2. precision profile

optional experimental 機能です。

含まれるもの:

- `blender_precision` MCP server
- precision template / schema
- `precise-blender-modeling` Skill
- subagent template
- dry-run / validation / visual QA の土台

## 3. 外部 3D サービス連携

`v1.2.0` では experimental 機能として扱います。

対象:

- Meshy
- Tripo AI
- Hyper3D Rodin
- Stability API SPAR3D

含まれるもの:

- Add-on Preferences の共通設定
- 3D View パネルの `External Services`
- `generate / poll / import` 共通 UI
- `plugin_bridge` 状態検査

## 4. plan mode

実際に変更する前に、installer が実行する予定 step を表示します。

```powershell
uv run blender-mcp-installer --plan
```

## 5. headless mode

GUI を使わずに installer step を実行します。

```powershell
uv run blender-mcp-installer --headless
```

ログ採取や検証環境での再現確認に使います。

## 6. 安全方針

- 公式 Blender MCP を中核にする
- 任意 Python / `bpy` 実行は通常導線では許可しない
- 既存 Codex 設定を書き換える前にバックアップを作る
- 危険操作は `preview -> confirm -> execute` を前提にする

## 7. 既知制約

- 外部 3D サービス連携は API キー未入手のため実験的公開
- SPAR3D の plugin bridge は未実装
- Poly Haven は provider 実装のみで UI は停止中
