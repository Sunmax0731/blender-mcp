# blender-mcp

公式 Blender MCP を前提に、Codex App と Codex CLI から Blender を扱うための導入・検証・運用を行うリポジトリです。

このリポジトリの主目的は次の 3 点です。
- 公式 `blender_mcp` add-on / MCP server を Windows 環境へ導入しやすくする
- Codex App から公式 MCP server を使って Blender を操作できるようにする
- Blender UI から Codex CLI に指示し、公式 add-on と干渉しない補助導線を整備する

## 基本方針

- Blender 側の中核機能は公式 `blender_mcp` を使う
- 独自 add-on / 独自 server は段階的に縮退し、公式構成との差分を最小化する
- 人が確認するドキュメント、Issue、コメントは日本語で管理する
- 開発は Issue 駆動で進め、工程切替時に `docs/` を見直す

## 参照

- 公式紹介: [Blender MCP Server](https://www.blender.org/lab/mcp-server/)
- 公式リポジトリ: [lab/blender_mcp](https://projects.blender.org/lab/blender_mcp)
- 公式リリース: [blender_mcp releases](https://projects.blender.org/lab/blender_mcp/releases)

2026-04-30 時点で確認した最新安定版は `v1.0.0` です。

## 現在の構成方針

### 1. Codex App から使う経路

`Codex App -> 公式 MCP server -> 公式 Blender add-on -> Blender`

- Codex App 側は MCP クライアントとして公式 server を利用する
- Blender 側では公式 add-on が TCP bridge server を提供する
- 3D 操作、スクリーンショット、サマリー取得などは可能な限り公式 tool を使う

### 2. Blender UI から使う経路

`Blender UI -> 補助ブリッジ -> Codex CLI -> 公式 Blender MCP / Blender`

- Blender の補助 UI は、公式 add-on を置き換えず補完する位置付けにする
- 自然言語入力は `Codex CLI` を優先する
- 補助 UI からの危険操作は `preview -> confirm -> execute` を守る

## セットアップ

### 1. Python 依存

```powershell
cd D:\Claude\MCP
uv sync --python 3.11 --extra dev
```

### 2. 公式 Blender MCP add-on の導入

PowerShell:

```powershell
cd D:\Claude\MCP
.\scripts\install_official_blender_mcp.ps1
```

コマンドプロンプト:

```bat
cd /d D:\Claude\MCP
scripts\install_official_blender_mcp.cmd
```

導入後の Blender 側確認:

1. `Edit > Preferences > Add-ons` を開く
2. `MCP` を検索して有効化する
3. Blender の `Online Access` を有効にする
4. add-on 設定で host / port / autostart を確認する

公式 add-on はローカル TCP bridge server を使うため、`Online Access` が無効だと起動できません。

### 3. テスト

```powershell
cd D:\Claude\MCP
uv run pytest
```

## ドキュメント

- [要件定義](D:/Claude/MCP/docs/requirements.md)
- [設計](D:/Claude/MCP/docs/design.md)
- [仕様](D:/Claude/MCP/docs/specification.md)
- [ロードマップ](D:/Claude/MCP/docs/roadmap.md)
- [検証計画](D:/Claude/MCP/docs/validation-plan.md)
- [リリース計画](D:/Claude/MCP/docs/release-plan.md)
- [運用ルール](D:/Claude/MCP/AGENTS.md)
- [必要スキル](D:/Claude/MCP/Skill.md)
