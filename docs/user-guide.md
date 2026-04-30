# 利用者向け利用方法

## 1. 基本の使い方

このツールは、公式 Blender MCP を使って Codex App から Blender を操作するための導入・補助ツールです。

基本の利用経路は次の通りです。

```text
Codex App -> 公式 Blender MCP server -> 公式 Blender add-on -> Blender
```

Blender を起動し、公式 `MCP` add-on が有効になっている状態で、Codex App から Blender に対する依頼を行います。

## 2. Codex App から Blender を操作する

Codex App では、Blender が起動している状態で Blender MCP tool を使います。

代表的な確認内容:

- Blender の現在状態を取得する
- viewport / window screenshot を取得する
- workspace を切り替える
- scene 内の object や material を確認する
- Blender 上にモデル、material、light、camera を作成する

依頼例:

```text
Blender で丸いキャラクターモデルを作成してください。体、手足、目、口、頬、マテリアル、ライト、カメラも設定してください。
```

```text
現在の Blender scene を確認し、モデルの構成、material、改善点を説明してください。
```

## 3. Blender UI から prompt を使う

Blender UI の補助導線では、prompt から制作指示を入力し、次の流れで実行します。

1. prompt を入力する
2. `Plan` で実行計画を作成する
3. Preview で変更内容を確認する
4. 問題なければ `Confirm` で承認する
5. `Execute` で Blender へ反映する
6. Result と Blender scene を確認する

危険操作や削除操作は、確認なしに実行しない方針です。

## 4. precision profile を使う

precision profile は optional experimental 機能です。

主な用途:

- モデル仕様を `model_spec` として明文化する
- validation report の形式を揃える
- visual QA の review view を計画する
- 高品質モデリング向け Skill / AGENTS / subagent template を配布する

v1.0.0 では、precision profile は正式な完成機能ではなく、今後の高品質モデリング支援に向けた土台として扱います。

## 5. うまく動かない場合の確認順

1. Blender が起動しているか
2. Blender の `MCP` add-on が有効か
3. Blender の `Online Access` が有効か
4. Codex App を再起動したか
5. installer のログに失敗がないか
6. `--plan` で導入ステップが表示されるか

詳細は [トラブルシュート](troubleshooting.md) を参照してください。
