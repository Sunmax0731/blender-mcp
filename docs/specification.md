# 仕様

## 1. 前提

- 対象 Blender: 5.1 系
- 対象 OS: Windows
- Python: 3.11 系
- パッケージ管理: `uv`
- 初期対応する公式 Blender MCP: `v1.0.0`
- このリポジトリの Release 版数: `v1.2.0`

## 2. 公式配布物

### 2.1 add-on / extension

- リリース資産: `mcp-1.0.0.zip`
- Blender 側では extension / add-on として導入する

### 2.2 server

- 公式 Git リポジトリから `v1.0.0` を専用 venv へ導入する

## 3. 本リポジトリが提供するもの

### 3.1 installer

- 公式 add-on の導入
- 公式 server の導入
- Codex 設定登録
- 公式 `mcp` の有効化
- 旧補助 UI 登録の cleanup
- 第三者 plugin の導入
- 補助 add-on の導入
- 任意で precision profile の導入

### 3.2 ドキュメント

- 利用者向け導入手順
- 利用者向け利用方法
- 既知制約とトラブルシュート
- 要件 / 仕様 / 設計 / 検証 / リリース計画

### 3.3 外部 3D サービス連携

- Preferences の共通設定
- 3D View の External Services パネル
- provider 実装
- plugin bridge helper

## 4. installer 仕様

### 4.1 主要 step

1. 公式 add-on を導入する
2. 公式 server を専用 venv に導入する
3. Codex 設定へ `blender-official` を登録する
4. Blender 側で公式 `mcp` を有効化する
5. 旧補助 UI を cleanup する
6. 第三者 plugin を導入する
7. 補助 add-on を導入する
8. 任意で precision profile を導入する
9. Blender を起動する

### 4.2 CLI オプション

- `--plan`
- `--headless`
- `--output-dir`
- `--no-launch-blender`
- `--include-precision-profile`
- `--skip-third-party-plugins`
- `--skip-plugin <key>`

### 4.3 配布 asset

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v1.2.0.json`

## 5. External Services 仕様

### 5.1 共通設定項目

- `enabled`
- `mode`
- `endpoint`
- `api_key`

### 5.2 共通操作

- `Preferences 読み込み`
- `Submit`
- `Poll`
- `Import`

### 5.3 provider 一覧

- Meshy
- Tripo AI
- Hyper3D Rodin
- Stability API SPAR3D
- Poly Haven provider 実装のみ

### 5.4 mode

- `cloud_api`
- `plugin_bridge`

### 5.5 `plugin_bridge` の現状

手動確認済み:

- Meshy
- Tripo AI
- Hyper3D Rodin

未対応:

- Stability API SPAR3D

## 6. 補助 add-on 仕様

### 6.1 Preferences

`Add-ons > Blender MCP > External Services` に provider ごとの設定を表示する。

### 6.2 3D View パネル

N パネルの `Blender MCP` タブに External Services セクションを表示する。

### 6.3 import helper

- `glb / gltf` を対象とする
- 指定 collection へ集約する

## 7. 既知制約

- 外部 3D サービス連携は experimental
- API キー未入手のため、`v1.2.0` は UI / plugin 導入 / plugin bridge 検証まで
- SPAR3D の plugin bridge は未実装
- Poly Haven は UI 非表示
