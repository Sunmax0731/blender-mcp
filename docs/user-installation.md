# 利用者向け導入手順

## 1. 対象

この手順は、Windows 上で Blender 5.1 系と Codex App を使う利用者向けです。

`v1.2.0` の installer は、公式 Blender MCP の導入に加えて、外部 3D サービス連携のための第三者 plugin と補助 add-on を同じフローで導入できます。

## 2. 事前準備

- Windows を利用している
- Blender 5.1 系をインストール済み
- Codex App をインストール済み
- インターネット接続がある
- Blender の `Online Access` を有効にできる
- Codex App と Blender を再起動できる

## 3. 推奨導入

1. GitHub Release から `blender-mcp-installer.exe` を取得する
2. `blender-mcp-installer.exe` を実行する
3. 画面上の変更対象を確認する
4. 必須チェックを有効にする
5. 必要に応じて第三者 plugin と precision profile を選ぶ
6. `Start Install` を押す
7. ログに失敗 step がないことを確認する
8. 完了後に `Finish` を押す
9. Codex App を再起動する
10. Blender を起動して導入結果を確認する

## 4. チェック項目の説明

### 4.1 `I reviewed the changes above and understand that local settings will be updated.`

必須です。

- Codex 設定
- Blender user preferences
- add-on / extension 配置

が更新されることを確認するためのチェックです。これを有効にしないと導入を開始できません。

### 4.2 `Also install supported third-party Blender plugins.`

外部 3D サービス連携に必要な Blender plugin を導入します。

対象:

- Meshy
- Tripo 3D
- RodinBridge

公式 Blender MCP だけ使う場合は外しても構いません。外部サービス連携を試す場合は有効にしてください。

### 4.3 plugin 個別チェック

第三者 plugin 導入を有効にした場合、各 plugin を個別に外せます。

使いどころ:

- 既に手動導入済みの plugin を再導入したくない
- 一部のサービスだけ試したい
- 問題切り分けのために対象を絞りたい

### 4.4 `Also install v2 precision profile templates, Skill, and subagent files.`

高品質モデリング支援用の optional experimental 機能です。

導入されるもの:

- `blender_precision` MCP server
- precision template / schema
- `precise-blender-modeling` Skill
- subagent template

通常の公式 Blender MCP 導入だけ使う場合は必須ではありません。

## 5. installer が実行する処理

標準では次の順で進みます。

1. 公式 Blender MCP add-on を導入する
2. 公式 Blender MCP server を専用 venv に導入する
3. Codex App へ `blender-official` を登録する
4. Blender 側で公式 `mcp` add-on を有効化する
5. 過去の補助 UI 登録を cleanup する
6. 第三者 plugin を導入する
7. 補助 Blender add-on を導入する
8. 任意で precision profile を導入する
9. 最後に Blender を起動する

## 6. 導入後の確認

### 6.1 Blender 側

1. `Edit > Preferences > Get Extensions` または `Add-ons` を開く
2. `MCP` が有効であることを確認する
3. `Meshy official plugin`、`Tripo 3D`、`RodinBridge` が必要に応じて有効であることを確認する
4. `Add-ons > Blender MCP` に External Services 設定が表示されることを確認する
5. 3D View の N パネルに `Blender MCP` タブが表示されることを確認する

### 6.2 Codex App 側

1. Codex App を再起動する
2. `blender-official` が表示されることを確認する
3. precision profile を導入した場合は `blender_precision` が表示されることを確認する

### 6.3 External Services 側

1. `Add-ons > Blender MCP > External Services` で対象サービスを有効化する
2. `mode` を `plugin_bridge` または `cloud_api` に設定する
3. 3D View の `Blender MCP > 外部サービス > Preferences 読み込み` を押す
4. `サービス概要` に状態が出ることを確認する

2026年5月1日時点で、手動確認済みの `plugin_bridge` 状態は次です。

- Meshy: `plugin_bridge ready (Meshy official plugin)`
- Tripo AI: `plugin_bridge ready (Tripo 3D)`
- Hyper3D Rodin: `plugin_bridge ready (RodinBridge)`
- Stability API SPAR3D: `plugin bridge 定義なし`

## 7. plan / headless モード

実行予定だけ確認する場合:

```powershell
uv run blender-mcp-installer --plan
```

GUI を使わず導入する場合:

```powershell
uv run blender-mcp-installer --headless
```

最後の Blender 起動を抑止する場合:

```powershell
uv run blender-mcp-installer --headless --no-launch-blender
```

第三者 plugin をスキップする場合:

```powershell
uv run blender-mcp-installer --headless --skip-third-party-plugins
```

一部 plugin だけ外す場合:

```powershell
uv run blender-mcp-installer --headless --skip-plugin meshy --skip-plugin rodin
```

precision profile を追加する場合:

```powershell
uv run blender-mcp-installer --headless --include-precision-profile
```

## 8. この Release の位置づけ

`v1.2.0` では外部 3D サービス連携を experimental として公開します。

できること:

- plugin 自動導入
- 補助 add-on 自動導入
- Preferences 設定
- `plugin_bridge` 状態確認
- 共通 UI の骨格利用

今回の Release 条件に含めていないこと:

- API キーを使った実サービス成功保証
- SPAR3D の plugin bridge
- Poly Haven の UI 再開
