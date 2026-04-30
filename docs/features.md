# 機能説明

## 1. 1クリック導入アプリ

Windows 向けに、公式 Blender MCP の導入をまとめて実行する GUI アプリです。

主な機能:

- 公式 Blender MCP add-on の導入
- 公式 Blender MCP server の専用仮想環境への導入
- Codex App の `blender-official` MCP server 登録
- Blender 側の公式 `mcp` add-on 有効化
- 旧開発版の不要な add-on 登録 cleanup
- 導入ログ表示
- 導入完了後の `Finish` 操作

## 2. plan mode

実際に変更する前に、installer が実行する予定の step を表示します。

```powershell
uv run blender-mcp-installer --plan
```

導入前確認やトラブルシュート時の手順確認に使います。

## 3. headless mode

GUI を使わずに installer step を実行します。

```powershell
uv run blender-mcp-installer --headless
```

ログ採取や検証環境での再現確認に使います。

## 4. Codex App 連携

Codex App に `blender-official` MCP server を登録します。

登録後は Codex App を再起動し、Blender を起動した状態で Blender MCP tool を使います。

## 5. Blender 側の画面

利用者が Blender 側で確認する画面は、公式 `MCP` add-on の Preferences です。モデル作成やシーン操作の指示は Codex App から行います。

installer は、過去の開発版で残った旧 `blender_mcp` add-on の不要な Preferences 登録がある場合に cleanup します。公式 `MCP` add-on は削除しません。

## 6. precision profile

precision profile は optional experimental 機能です。

含まれるもの:

- precision template / schema
- `blender-precision-mcp` sidecar scaffold
- `model_spec`
- `validation_report`
- `addon_registry`
- visual QA manifest
- Skill / AGENTS / subagent template

v1 系では、precision profile 導入時に `blender_precision` MCP server を自動登録しません。`blender-precision-mcp` は experimental scaffold であり、standalone `uvx` package としてはまだ配布していないためです。

## 7. 安全方針

- 公式 Blender MCP を中核にする
- 独自 add-on / server は利用者向け導線から外す
- 任意 Python / `bpy` 実行を通常導線では許可しない
- 既存 Codex 設定を変更する場合はバックアップを作成する
- 外部公開前提の常駐 server 構成にしない
