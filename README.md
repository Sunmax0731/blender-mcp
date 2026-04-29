# blender-mcp

公式 Blender MCP を前提に、Codex App と Codex CLI から Blender を扱うための導入・検証・運用を行うリポジトリです。

このリポジトリの主目的は次の 3 点です。
- 公式 `blender_mcp` add-on / MCP server を Windows 環境へ導入しやすくする
- Codex App から公式 MCP server を使って Blender を操作できるようにする
- Blender UI から Codex CLI に指示し、公式 add-on と干渉しない補助導線を整備する

直近の Release 成果物は、1 クリックで次を進められる Windows 向け導入アプリです。
- Codex への `blender-official` MCP server 登録
- Blender への公式 `mcp` add-on 導入
- 公式 `mcp` の有効化と legacy `blender_mcp` の無効化補助

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

1. `Edit > Preferences > Get Extensions` を開く
2. `MCP` を検索して表示されることを確認する
3. Blender の `Online Access` を有効にする
4. add-on 設定で host / port / autostart を確認する

公式 add-on はローカル TCP bridge server を使うため、`Online Access` が無効だと起動できません。
このスクリプトは Blender 5.1 の extension 管理経路 `user_default` へ導入します。

有効化を自動化したい場合:

```powershell
cd D:\Claude\MCP
.\scripts\enable_official_blender_mcp_addon.ps1
```

- 公式 `mcp` add-on を有効化する
- legacy `blender_mcp` add-on が有効なら無効化する
- Blender 5.1 extension key `bl_ext.*.mcp` にも対応する
- `host=localhost` `port=9876` `autostart=True` を確認できる

### 3. テスト

```powershell
cd D:\Claude\MCP
uv run pytest
```

### 4. 公式 Blender MCP server の導入

PowerShell:

```powershell
cd D:\Claude\MCP
.\scripts\install_official_blender_mcp_server.ps1
```

コマンドプロンプト:

```bat
cd /d D:\Claude\MCP
scripts\install_official_blender_mcp_server.cmd
```

- 公式 server は repo の `.venv` ではなく `D:\Claude\MCP\.official-mcp-venv` に導入する
- これにより、repo 内の legacy 実装依存と競合させない

### 5. Codex App への登録

PowerShell:

```powershell
cd D:\Claude\MCP
.\scripts\register_official_blender_mcp_in_codex.ps1
```

- `C:\Users\gkkjh\.codex\config.toml` に `mcp_servers.blender-official` を追記する
- 実行前にバックアップを作成する
- 反映には Codex App の再起動が必要
- 起動スクリプト側で `BLENDER_PATH` を自動解決するため、Steam 配置や通常配置でも使いやすい

設定例:

- [Codex MCP 設定例](D:/Claude/MCP/docs/codex-mcp-config-example.toml)

### 6. 1クリック導入アプリ

開発版アプリを起動する場合:

```powershell
cd D:\Claude\MCP
uv run blender-mcp-installer
```

実行予定ステップだけ確認する場合:

```powershell
cd D:\Claude\MCP
uv run blender-mcp-installer --plan
```

GUI を使わず導入ログを採取する場合:

```powershell
cd D:\Claude\MCP
uv run blender-mcp-installer --headless
```

`exe` を生成する場合:

```powershell
cd D:\Claude\MCP
uv sync --python 3.11 --extra dev
.\scripts\build_installer_exe.ps1
```

- GUI から導入開始、進捗確認、ログ確認ができる
- 内部では既存 PowerShell スクリプトを順番に実行する
- headless 実行では `artifacts/one-click-installer/` 配下へログを残せる
- `exe` は `dist/one-click-installer/` 配下へ生成する

## ドキュメント

- [要件定義](D:/Claude/MCP/docs/requirements.md)
- [設計](D:/Claude/MCP/docs/design.md)
- [仕様](D:/Claude/MCP/docs/specification.md)
- [ロードマップ](D:/Claude/MCP/docs/roadmap.md)
- [検証計画](D:/Claude/MCP/docs/validation-plan.md)
- [リリース計画](D:/Claude/MCP/docs/release-plan.md)
- [旧独自構成の在庫](D:/Claude/MCP/docs/legacy-inventory.md)
- [運用ルール](D:/Claude/MCP/AGENTS.md)
- [必要スキル](D:/Claude/MCP/Skill.md)
