# 利用者向け利用方法

## 1. 基本の使い方

このツールは、公式 Blender MCP を使って Codex App から Blender を操作するための導入・補助ツールです。

基本の利用経路は次の通りです。

```text
Codex App -> 公式 Blender MCP server -> 公式 Blender add-on -> Blender
```

Blender を起動し、公式 `MCP` add-on が有効な状態で、Codex App から Blender に対する依頼を行います。

## 2. Codex App から Blender を操作する

Codex App では、Blender が起動している状態で Blender MCP tool を使います。

代表的な確認・操作:

- Blender の現在状態を取得する
- viewport / window screenshot を取得する
- scene 内の object や material を確認する
- Blender 上にモデル、material、light、camera を作成する

依頼例:

```text
Blenderで丸いキャラクターモデルを作成してください。体、手足、目、口、頬、マテリアル、ライト、カメラも設定してください。
```

```text
現在の Blender scene を確認し、モデルの構成、material、改善点を説明してください。
```

## 3. Blender 側で確認する場所

Blender 側では、次を確認します。

1. `Edit > Preferences > Add-ons` または `Get Extensions` を開く
2. `MCP` が導入済みで有効になっていることを確認する
3. `Host`、`Port`、`Auto Start` を確認する
4. `Server is running` と表示されることを確認する

v1 系では、Blender の N メニューに独自の Prompt UI は表示しません。自然言語での指示は Codex App から行ってください。

## 4. precision profile を使う

precision profile は optional experimental 機能です。

主な用途:

- モデル仕様を `model_spec` として明文化する
- validation report の形式を揃える
- visual QA の review view を計画する
- 高品質モデリング向け Skill / AGENTS / subagent template を配布する

通常の公式 Blender MCP 導入だけを使う場合は、precision profile を有効にする必要はありません。

## 5. 動かない場合の確認順

1. Blender が起動しているか
2. Blender の `MCP` add-on が有効か
3. Blender の `Online Access` が有効か
4. Codex App を再起動したか
5. installer のログに失敗がないか
6. `--plan` で導入ステップが表示されるか

詳細は [トラブルシュート](troubleshooting.md) を参照してください。
