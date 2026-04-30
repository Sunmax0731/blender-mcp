# blender-mcp

公式 Blender MCP を前提に、Codex App と Codex CLI から Blender を扱うための導入・検証・運用を行うリポジトリです。

このリポジトリの主目的は次の 3 点です。
- 公式 `blender_mcp` add-on / MCP server を Windows 環境へ導入しやすくする
- Codex App から公式 MCP server を使って Blender を操作できるようにする
- Blender UI から Codex CLI に指示し、公式 add-on と干渉しない補助導線を整備する

直近の Release 成果物は、1 クリックで次を進められる Windows 向け導入アプリです。
- Codex への `blender-official` MCP server 登録
- Blender への公式 `mcp` add-on 導入
- 公式 `mcp` の有効化

## 基本方針

- Blender 側の中核機能は公式 `blender_mcp` を使う
- 独自 add-on / 独自 server は段階的に縮退し、公式構成との差分を最小化する
- 人が確認するドキュメント、Issue、コメントは日本語で管理する
- 開発は Issue 駆動で進め、工程切替時に `docs/` を見直す

## 参照

- 公式紹介: [Blender MCP Server](https://www.blender.org/lab/mcp-server/)
- 公式リポジトリ: [lab/blender_mcp](https://projects.blender.org/lab/blender_mcp)
- 公式リリース: [blender_mcp releases](https://projects.blender.org/lab/blender_mcp/releases)

このリポジトリの初期対応版は、2026-04-30 時点で確認した公式 Blender MCP `v1.0.0` です。
このリポジトリの初回 GitHub Release 版数は `v0.1.0` を予定しています。

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

以下のコマンドは、clone したリポジトリのルートで実行してください。

```powershell
Set-Location <repo>
```

コマンドプロンプトを使う場合:

```bat
cd /d <repo>
```

`<repo>` は、このリポジトリを clone または展開したディレクトリに置き換えてください。

### 1. 1クリック導入アプリ

Release 版を使う場合は、GitHub Release から `blender-mcp-installer.exe` を取得して実行します。
開発版をリポジトリから起動する場合:

```powershell
uv run blender-mcp-installer
```

- GUI から導入開始、進捗確認、ログ確認ができる
- Codex 設定、公式 Blender MCP server、Blender add-on の導入を順番に実行する
- 導入完了後は Blender を自動起動して、そのまま手動確認へ移れる

実行予定ステップだけ確認する場合:

```powershell
uv run blender-mcp-installer --plan
```

GUI を使わず導入ログを採取する場合:

```powershell
uv run blender-mcp-installer --headless
```

GUI を使わず導入し、最後の Blender 起動だけ抑止する場合:

```powershell
uv run blender-mcp-installer --headless --no-launch-blender
```

headless 実行では `artifacts/one-click-installer/` 配下へログを残せます。

### 2. 導入後の確認

Blender 側:

1. `Edit > Preferences > Get Extensions` を開く
2. `MCP` が導入済みで有効になっていることを確認する
3. Blender の `Online Access` が有効になっていることを確認する
4. add-on 設定で host / port / autostart を確認する

Codex App 側:

1. Codex App を再起動する
2. `blender-official` MCP server が利用できることを確認する
3. Blender を起動した状態で、MCP tool から状態取得やスクリーンショット取得を試す

公式 add-on はローカル TCP bridge server を使うため、`Online Access` が無効だと起動できません。

### 3. 手動導入

1クリック導入アプリを使わずに個別ステップを実行したい場合の手順です。

#### Python 依存

```powershell
uv sync --python 3.11 --extra dev
```

#### 公式 Blender MCP add-on の導入

PowerShell:

```powershell
.\scripts\install_official_blender_mcp.ps1
```

コマンドプロンプト:

```bat
scripts\install_official_blender_mcp.cmd
```

有効化を自動化したい場合:

```powershell
.\scripts\enable_official_blender_mcp_addon.ps1
```

- 公式 `mcp` add-on を有効化する
- Blender 5.1 extension key `bl_ext.*.mcp` にも対応する
- `host=localhost` `port=9876` `autostart=True` を確認できる

#### 公式 Blender MCP server の導入

PowerShell:

```powershell
.\scripts\install_official_blender_mcp_server.ps1
```

コマンドプロンプト:

```bat
scripts\install_official_blender_mcp_server.cmd
```

- 公式 server は repo の `.venv` ではなく `.official-mcp-venv/` に導入する
- これにより、repo 内の開発用 Python 依存と競合させない

#### Codex App への登録

PowerShell:

```powershell
.\scripts\register_official_blender_mcp_in_codex.ps1
```

- `%USERPROFILE%\.codex\config.toml` に `mcp_servers.blender-official` を追記する
- 実行前にバックアップを作成する
- 反映には Codex App の再起動が必要
- 起動スクリプト側で `BLENDER_PATH` を自動解決するため、Steam 配置や通常配置でも使いやすい

設定例:

- [Codex MCP 設定例](docs/codex-mcp-config-example.toml)

### 4. 開発者向け

テスト:

```powershell
uv run pytest
```

`exe` を生成する場合:

```powershell
uv sync --python 3.11 --extra dev
.\scripts\build_installer_exe.ps1
```

- `exe` は `dist/one-click-installer/` 配下へ生成する

初回 GitHub Release では、主配布物として `blender-mcp-installer.exe` を添付します。
公式 Blender MCP の `mcp-1.0.0.zip` は、このリポジトリの Release asset としては再配布しません。

## ドキュメント

- [要件定義](docs/requirements.md)
- [設計](docs/design.md)
- [仕様](docs/specification.md)
- [ロードマップ](docs/roadmap.md)
- [検証計画](docs/validation-plan.md)
- [リリース計画](docs/release-plan.md)
- [Blender MCP 実行例](docs/examples.md)
- [配布用 Skill](docs/skills.md)
- [初回 Release ノート案](docs/release-notes-v0.1.0.md)
- [運用ルール](AGENTS.md)
- [必要スキル](Skill.md)
