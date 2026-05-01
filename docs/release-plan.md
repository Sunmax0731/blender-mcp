# リリース計画

## 1. 対象 Release

- リポジトリ版数: `v1.2.0`
- 位置づけ: experimental external services release
- 公式 Blender MCP 対応版: `v1.0.0`

## 2. リリースに含めるもの

### 2.1 正式機能

- 公式 Blender MCP の導入
- `blender-official` の Codex App 登録
- 公式 `mcp` add-on の有効化
- cleanup step
- 第三者 plugin 自動導入
- 補助 add-on 自動導入
- precision profile の任意導入

### 2.2 experimental 機能

- Meshy / Tripo AI / Hyper3D Rodin / Stability API SPAR3D の External Services UI
- provider 層
- `plugin_bridge` 状態確認
- `generate / poll / import` 共通 UI 骨格

## 3. リリースに含めないもの

- API キー未入手状態での外部サービス成功保証
- SPAR3D の plugin bridge
- Poly Haven の UI 再開
- Blender 本体、Codex App 本体の同梱

## 4. 配布 asset

- `dist/one-click-installer/blender-mcp-installer.exe`
- `dist/one-click-installer/blender-mcp-installer.exe.sha256`
- `dist/one-click-installer/release-manifest-v1.2.0.json`

## 5. リリース前チェック

### 5.1 自動確認

- `uv run pytest`
- `uv run blender-mcp-installer --plan`
- `uv run blender-mcp-installer --plan --skip-third-party-plugins --no-launch-blender`
- `uv run python -m compileall src blender_addon`

### 5.2 手動確認

- installer が完走する
- Blender に `MCP` が入る
- Blender に `Blender MCP` が入る
- Meshy / Tripo / Rodin plugin が入る
- `サービス概要` に `plugin_bridge ready` が出る

## 6. 公開時に明記すること

- 外部 3D サービス連携は experimental であること
- API キー未入手のため今回の Release 条件は UI / installer / plugin bridge までであること
- SPAR3D は plugin bridge 未対応であること
- RodinBridge が debug console を開く場合があること

## 7. 公開手順

1. docs を `v1.2.0` 状態へ更新する
2. version を更新する
3. テストと compileall を実行する
4. installer をビルドする
5. sha256 と release manifest を生成する
6. GitHub Release `v1.2.0` を作成する
