# 利用者向け利用方法

## 1. 基本の使い方

通常の主経路は次です。

```text
Codex App -> 公式 Blender MCP server -> 公式 Blender add-on -> Blender
```

Blender は起動したままにし、Codex App から scene 確認、screenshot 取得、モデリング指示を行います。

## 2. Codex App から使う

代表的な用途:

- scene 状態の取得
- screenshot の取得
- object / material / camera / light の確認
- Blender 上のモデル作成と更新

依頼例:

```text
Blenderで丸いキャラクターモデルを作成してください。体、手足、目、口、頬、ライト、カメラを設定し、最後に構成を説明してください。
```

```text
現在の scene を確認し、object 構成、material、改善点を日本語でまとめてください。
```

## 3. Blender 側で確認する場所

### 3.1 公式 MCP

1. `Edit > Preferences > Add-ons` または `Get Extensions` を開く
2. `MCP` が有効であることを確認する
3. `Host`、`Port`、`Auto Start` を確認する
4. `Server is running` が表示されることを確認する

### 3.2 補助 add-on

1. `Add-ons > Blender MCP` を開く
2. `External Services` 設定が表示されることを確認する
3. 使うサービスの `enabled / mode / endpoint / api_key` を設定する

### 3.3 3D View の Blender MCP パネル

1. 3D View の N パネルを開く
2. `Blender MCP` タブを開く
3. `外部サービス > Preferences 読み込み` を押す
4. `サービス概要` を確認する

## 4. External Services の使い方

`v1.2.0` 時点では experimental 機能です。

### 4.1 `plugin_bridge`

Blender plugin を経由して使うモードです。

向いているケース:

- 既に公式または配布元 plugin を使っている
- add-on 側が持つ operator を使いたい
- API 契約より Blender plugin を優先したい

確認できること:

- add-on の検出
- add-on の有効化状態
- 必須 operator の有無

手動確認済み:

- Meshy
- Tripo AI
- Hyper3D Rodin

未対応:

- Stability API SPAR3D

### 4.2 `cloud_api`

provider 実装から API を直接呼ぶモードです。

主な UI:

- `Submit`
- `Poll`
- `Import`

利用前提:

- API キーを持っている
- endpoint を確認済み
- 一部サービスでは JSON 追加パラメータを与える

## 5. 生成系 UI の意味

### `Submit`

生成ジョブを投げます。

### `Poll`

ジョブ状態を確認します。

### `Import`

完了済みの `result_url` から `glb / gltf` を取得し、指定 collection に import します。

既定 collection:

- `Generated_External_Assets`

## 6. precision profile を使う場合

precision profile は optional experimental 機能です。

おすすめの使い順:

1. `blender-official` で接続確認する
2. `blender_precision` で dry-run や validation を試す
3. live 処理は Blender 側実行経路で行う

`blender_precision` で `blender_unavailable` が返る場合は、sidecar が `bpy` を直接保持していないだけで、導入失敗とは限りません。

## 7. 既知制約

- 外部 3D サービス連携は experimental
- API キー未入手のため、今回の Release は UI / installer / plugin bridge 検証まで
- SPAR3D は plugin bridge 未対応
- Poly Haven は provider 実装を保持しているが UI からは非表示
- RodinBridge は debug console を開く場合がある

## 8. 困ったとき

次を順に確認してください。

1. Blender が起動しているか
2. `MCP` add-on が有効か
3. `Online Access` が有効か
4. Codex App を再起動したか
5. `Blender MCP > 外部サービス > Preferences 読み込み` を押したか
6. `サービス概要` に `plugin_bridge ready` が出るか

詳細は [トラブルシュート](troubleshooting.md) を参照してください。
