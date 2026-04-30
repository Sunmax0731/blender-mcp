# blender-mcp

公式 Blender MCP を前提に、Codex App と Codex CLI から Blender を扱うための導入・検証・運用を行うリポジトリです。

このリポジトリの主目的は次の 3 点です。
- 公式 `blender_mcp` add-on / MCP server を Windows 環境へ導入しやすくする
- Codex App から公式 MCP server を使って Blender を操作できるようにする
- v2 以降の高品質モデリング支援に向けた template / Skill / 検証方針を整理する

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
このリポジトリの正式 Release は [`v1.0.3`](https://github.com/Sunmax0731/blender-mcp/releases/tag/v1.0.3) です。

## 現在の構成方針

### 1. Codex App から使う経路

`Codex App -> 公式 MCP server -> 公式 Blender add-on -> Blender`

- Codex App 側は MCP クライアントとして公式 server を利用する
- Blender 側では公式 add-on が TCP bridge server を提供する
- 3D 操作、スクリーンショット、サマリー取得などは可能な限り公式 tool を使う

### 2. Blender 側の画面

v1 系では、Blender の N メニューに独自の補助 Prompt UI は表示しません。
Blender 側では公式 `MCP` add-on の Preferences を確認し、モデリング指示は Codex App から行います。

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

Release 版を使う場合は、[`v1.0.3` Release](https://github.com/Sunmax0731/blender-mcp/releases/tag/v1.0.3) から `blender-mcp-installer.exe` を取得して実行します。
導入手順は [利用者向け導入手順](docs/user-installation.md)、使い方は [利用者向け利用方法](docs/user-guide.md) を参照してください。
開発版をリポジトリから起動する場合:

```powershell
uv run blender-mcp-installer
```

- GUI から導入開始、進捗確認、ログ確認ができる
- Codex 設定、公式 Blender MCP server、Blender add-on の導入を順番に実行する
- 既存環境に残った旧補助 Prompt UI の登録を削除する
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

v2 precision profile を任意で導入する場合:

```powershell
uv run blender-mcp-installer --headless --include-precision-profile
```

precision profile は、Codex 用 template、Skill、subagent template を追加する任意導線です。通常の公式 Blender MCP 導入だけを使う場合は有効にする必要はありません。
precision profile を導入した場合も、最初の確認は `blender-official` から始めます。`blender_precision` は dry-run、static validation、artifact 設計にはそのまま使えますが、scene 生成や review image 保存のように `bpy` を必要とする live 処理は Blender 側実行経路で行います。

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
4. precision profile を導入した場合は `blender_precision` MCP server が利用できることを確認する
5. `blender_precision` では、まず dry-run で `model_spec` と予定操作を確認する
6. live 生成や validation artifact 採取が必要な場合は、Blender background 実行または Blender 接続済み経路で実行する

公式 add-on はローカル TCP bridge server を使うため、`Online Access` が無効だと起動できません。
`blender_precision` で `error.code=blender_unavailable` が返る場合は、sidecar プロセスから `bpy` へ直接は触れていません。Blender を起動したうえで、公式 MCP 接続確認後に live 実行経路へ切り替えてください。

### 3. 手動導入

1クリック導入アプリを使わずに個別ステップを実行したい場合の手順です。

#### Python 依存

```powershell
uv sync --python 3.11 --extra dev
```

#### base-character-package の VRM を `.blend` へ変換

```powershell
uv run python .\scripts\convert_vrm_to_blend.py
```

- `templates/precision/base_character_package/BaseAvatar.vrm` を既定入力に使う
- 最新の `VRM Add-on for Blender` release zip を取得し、Blender background で install と import を行う
- `artifacts/vrm-base-character-convert/` に `.blend`、conversion report、object list を保存する

#### 変換済み `.blend` から base asset manifest を生成

```powershell
uv run python .\scripts\analyze_base_character_blend.py
```

- 既定では `artifacts/vrm-base-character-convert/exports/BaseAvatar.blend` を入力に使う
- `artifacts/base-character-analysis/` に `base_asset_manifest.json`、`adaptation_plan.json`、`object_list.json` を保存する

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

旧補助 Prompt UI の登録だけを削除したい場合:

```powershell
.\scripts\remove_blender_prompt_ui.ps1
```

- 公式 `MCP` add-on は残す
- 旧 `blender_mcp` add-on の Preferences 登録が残っている場合だけ削除する

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

初回 GitHub Release では、[`v0.1.0`](https://github.com/Sunmax0731/blender-mcp/releases/tag/v0.1.0) に主配布物として `blender-mcp-installer.exe` を添付しています。
公式 Blender MCP の `mcp-1.0.0.zip` は、このリポジトリの Release asset としては再配布しません。

## ドキュメント

利用者向け:

- [利用者向け導入手順](docs/user-installation.md)
- [利用者向け利用方法](docs/user-guide.md)
- [機能説明](docs/features.md)
- [トラブルシュート](docs/troubleshooting.md)

v1.0.0 Release 準備:

- [v1.0.0 release scope](docs/release-scope-v1.0.0.md)
- [v1.0.0 release milestone plan](docs/release-milestones-v1.0.0.md)
- [v1.0.0 installer safety checklist](docs/installer-safety-v1.0.0.md)
- [v1.0.0 release manifest](docs/release-manifest-v1.0.0.md)
- [v1.0.0 Release notes](docs/release-notes-v1.0.0.md)
- [v1.0.1 release manifest](docs/release-manifest-v1.0.1.md)
- [v1.0.1 Release notes](docs/release-notes-v1.0.1.md)
- [v1.0.2 release manifest](docs/release-manifest-v1.0.2.md)
- [v1.0.2 Release notes](docs/release-notes-v1.0.2.md)
- [v1.0.3 release manifest](docs/release-manifest-v1.0.3.md)
- [v1.0.3 Release notes](docs/release-notes-v1.0.3.md)

設計・開発者向け:

- [要件定義](docs/requirements.md)
- [設計](docs/design.md)
- [仕様](docs/specification.md)
- [ロードマップ](docs/roadmap.md)
- [v2 精密モデリング完成ロードマップ](docs/v2-precision-roadmap.md)
- [v2 precision template / schema](docs/precision-templates.md)
- [検証計画](docs/validation-plan.md)
- [リリース計画](docs/release-plan.md)
- [v2 release validation](docs/release-validation-v2.md)
- [Blender MCP 実行例](docs/examples.md)
- [配布用 Skill](docs/skills.md)
- [運用ルール](AGENTS.md)
- [必要スキル](Skill.md)
