# blender-mcp

公式 Blender MCP を前提に、Codex App / Codex CLI から Blender を扱うための導入、統合、検証、配布を行うリポジトリです。

`v1.2.0` は、公式 Blender MCP 導入基盤に加えて、外部 3D サービス連携の補助 UI と plugin 自動導入を experimental 機能として含む Release です。

## 現在の Release

- このリポジトリの最新 Release: [`v1.2.0`](https://github.com/Sunmax0731/blender-mcp/releases/tag/v1.2.0)
- 初期対応している公式 Blender MCP: `v1.0.0`
- 対象 OS: Windows
- 対象 Blender: 5.1 系

## 基本方針

- Blender 側の中核機能は公式 `blender_mcp` を使う
- このリポジトリは導入、Codex 統合、自動化、検証、配布を担う
- 危険操作は `preview -> confirm -> execute` を原則にする
- 人が確認する docs / Issue / comment は日本語で整備する

## 提供するもの

### 1. 1クリック導入アプリ

Windows 向けの `blender-mcp-installer.exe` を提供します。主な処理は次です。

- 公式 Blender MCP add-on の導入
- 公式 Blender MCP server の専用 venv への導入
- Codex App への `blender-official` MCP server 登録
- Blender 側での公式 `mcp` add-on 有効化
- 旧補助 UI 登録の cleanup
- Meshy / Tripo / Rodin plugin の自動導入
- 補助 Blender add-on の自動導入
- 任意で precision profile の導入

### 2. precision profile

`blender_precision` MCP server、template、Skill、subagent template を任意で追加できます。

これは通常導線では必須ではありません。高品質モデリング向けの dry-run、validation、visual QA、export 管理を使いたい場合だけ有効にしてください。

### 3. 外部 3D サービス連携

`v1.2.0` 時点では experimental 機能です。

- Meshy
- Tripo AI
- Hyper3D Rodin
- Stability API SPAR3D

含まれるもの:

- Add-on Preferences での `enabled / mode / endpoint / api_key` 管理
- 3D View の `Blender MCP` パネルでの `Preferences 読み込み`
- `plugin_bridge` の状態概要表示
- `generate / poll / import` 共通 UI の骨格

含まれないもの:

- API キーなしでの実サービス成功保証
- SPAR3D の plugin bridge
- Poly Haven の再開 UI

## 利用経路

### Codex App から使う主経路

```text
Codex App -> 公式 Blender MCP server -> 公式 Blender add-on -> Blender
```

### Blender 側の補助経路

```text
Blender UI -> 補助 add-on -> provider / plugin_bridge helper
```

補助 add-on は、公式 MCP を置き換えるものではなく、外部サービス設定と状態表示を補うための層です。

## 導入方法

Release 版を使う場合は [`v1.2.0` Release](https://github.com/Sunmax0731/blender-mcp/releases/tag/v1.2.0) から `blender-mcp-installer.exe` を取得してください。

詳しい導入手順:

- [利用者向け導入手順](docs/user-installation.md)
- [利用者向け利用方法](docs/user-guide.md)
- [トラブルシュート](docs/troubleshooting.md)

## installer のチェック項目

### `I reviewed the changes above...`

ローカル設定が更新されることを確認するための必須チェックです。これを有効にしないと導入を開始できません。

### `Also install supported third-party Blender plugins.`

Meshy / Tripo / Rodin の Blender plugin を導入します。外部サービス連携を試す場合は有効にしてください。公式 Blender MCP だけ使う場合は外しても構いません。

### plugin 個別チェック

第三者 plugin 導入を有効にした場合、Meshy / Tripo / Rodin を個別に外せます。既に別経路で導入済みの場合や、一部だけ試したい場合に使います。

### `Also install v2 precision profile templates, Skill, and subagent files.`

`blender_precision` MCP server と関連 template を追加します。通常利用では必須ではありません。

## 導入後の確認

### Blender 側

1. `Edit > Preferences > Get Extensions` または `Add-ons` を開く
2. `MCP` が有効であることを確認する
3. 必要なら `Meshy official plugin`、`Tripo 3D`、`RodinBridge` が有効であることを確認する
4. `Add-ons > Blender MCP` に External Services 設定が出ることを確認する
5. 3D View の N パネルに `Blender MCP` タブがあることを確認する

### Codex App 側

1. Codex App を再起動する
2. `blender-official` が有効であることを確認する
3. precision profile を導入した場合は `blender_precision` が有効であることを確認する
4. Blender 起動中に screenshot 取得や scene 状態取得を試す

### External Services 側

1. `Add-ons > Blender MCP > External Services` で使うサービスを有効化する
2. `mode` を `plugin_bridge` または `cloud_api` に設定する
3. 3D View の `Blender MCP > 外部サービス > Preferences 読み込み` を押す
4. `サービス概要` に `plugin_bridge ready` などの状態が出ることを確認する

## 開発者向けコマンド

依存同期:

```powershell
cd D:\Claude\MCP
uv sync --python 3.11 --extra dev
```

テスト:

```powershell
cd D:\Claude\MCP
uv run pytest
```

plan mode:

```powershell
cd D:\Claude\MCP
uv run blender-mcp-installer --plan
```

installer の exe 再生成:

```powershell
cd D:\Claude\MCP
.\scripts\build_installer_exe.ps1
```

## 関連ドキュメント

- [機能説明](docs/features.md)
- [要件定義](docs/requirements.md)
- [仕様](docs/specification.md)
- [設計](docs/design.md)
- [ロードマップ](docs/roadmap.md)
- [検証計画](docs/validation-plan.md)
- [リリース計画](docs/release-plan.md)
- [v1.2.0 Release notes](docs/release-notes-v1.2.0.md)
- [v1.2.0 release manifest](docs/release-manifest-v1.2.0.md)

## 既知制約

- 外部 3D サービス連携は experimental であり、API キー未入手のため実サービス成功までは今回の Release 条件に含めていません
- SPAR3D は `cloud_api` の UI と provider 骨格までで、plugin bridge は未実装です
- Poly Haven は provider 実装を保持していますが、現時点では UI から非表示です
- RodinBridge は add-on 側の debug console を開く場合があります
