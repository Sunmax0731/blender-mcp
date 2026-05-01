# 検証計画

## 1. 目的

- 公式 Blender MCP を前提とした導入手順が再現できることを確認する
- installer から公式 MCP、第三者 plugin、補助 add-on を一括導入できることを確認する
- docs と実装が一致していることを確認する
- external services の experimental 範囲と既知制約を明確化する

## 2. 検証レベル

### 2.1 静的確認

- docs の日本語表記確認
- version と release 名称の一致確認
- installer step と docs の一致確認
- release asset 一覧の確認

### 2.2 installer 確認

- 公式 add-on が導入できる
- 公式 server が専用 venv に導入できる
- `blender-official` が Codex 設定へ登録される
- 公式 `mcp` add-on が有効化される
- cleanup step が成功する
- 第三者 plugin が導入できる
- 補助 add-on が導入できる
- 任意で precision profile を導入できる

### 2.3 Blender 側確認

- `MCP` add-on が有効である
- `Blender MCP` add-on が有効である
- 3D View の N パネルに `Blender MCP` タブが表示される
- `Add-ons > Blender MCP > External Services` が表示される

### 2.4 External Services 確認

- `Preferences 読み込み` で設定が反映される
- `サービス概要` に provider 状態が表示される
- Meshy / Tripo / Rodin で `plugin_bridge ready` が表示される
- SPAR3D は `plugin bridge 定義なし` と表示される

### 2.5 Codex App 側確認

- `blender-official` が利用できる
- precision profile を入れた場合は `blender_precision` が利用できる

## 3. 手動確認済み事項

2026年5月1日時点で次を確認済み。

- installer が第三者 plugin を導入できる
- installer が補助 add-on を導入できる
- Blender Preferences に External Services 設定が表示される
- 3D View に `Blender MCP` タブが表示される
- `サービス概要` に次が出る
  - Meshy: `plugin_bridge ready (Meshy official plugin)`
  - Tripo AI: `plugin_bridge ready (Tripo 3D)`
  - Hyper3D Rodin: `plugin_bridge ready (RodinBridge)`
  - Stability API SPAR3D: `plugin bridge 定義なし`

## 4. 自動確認

Release 前に少なくとも次を実行する。

```powershell
uv run pytest
```

```powershell
uv run blender-mcp-installer --plan
```

```powershell
uv run blender-mcp-installer --plan --skip-third-party-plugins --no-launch-blender
```

```powershell
uv run python -m compileall src blender_addon
```

## 5. `v1.2.0` で Release 条件に含めないもの

- API キー前提の実サービス成功
- SPAR3D の plugin bridge
- Poly Haven の UI 再開

これらは experimental 範囲または次工程として扱う。

## 6. 証跡

- `installer.log`
- Blender の Add-ons / Get Extensions 画面
- Blender の `Blender MCP` パネル画面
- GitHub Issue コメント
- release notes と release manifest
