# v2 精密モデリング完成ロードマップ

## 1. 目的

v2 では、公式 Blender MCP を土台に、Codex からより高品質なモデリング、検証、視覚レビュー、承認済み add-on 活用を行える実装を段階的に完成させる。

利用者向けの主経路は次を前提にする。

- Codex App からの指示
- Blender 側は公式 `MCP` add-on の設定確認
- live 処理は Blender 実行コンテキストまたは official MCP 接続経路で実行

## 2. 設計原則

- `command` / `args` は MCP server 起動設定として使う
- tool の公開制御は sidecar の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で行う
- `args` では profile / config / tool pack を渡し、tool 実行引数は `tools/call.arguments` で扱う
- `bpy.ops` / `bpy.context` / context override は add-on integration 専用責務として分離する
- 危険操作は `preview -> confirm -> execute` を守る

## 3. 現在地

2026-04-30 時点で実装済みの主な範囲は次のとおり。

- precision profile / sidecar scaffold
- `character_spec` / `pipeline_spec` の正規化
- 類型別 template / library
- validator 骨格
- live scene build と strict validation
- live rig / shape key / weight bridge
- `BaseAvatar.vrm -> BaseAvatar.blend` 変換
- `.blend` から `base_asset_manifest.json` / `adaptation_plan.json` 生成

未完了で、テスト工程の前に必要な実装は次のとおり。

1. [#151](https://github.com/Sunmax0731/blender-mcp/issues/151) base asset manifest を auto character pipeline に接続する
2. [#153](https://github.com/Sunmax0731/blender-mcp/issues/153) 画像入力から `character_spec` 補強と `image_reference_manifest` を生成する
3. [#154](https://github.com/Sunmax0731/blender-mcp/issues/154) hair preset library と live hair build を追加する
4. [#155](https://github.com/Sunmax0731/blender-mcp/issues/155) auto-fix retry loop と stage retry traceability を追加する

関連する要件判断の残件:

- [#148](https://github.com/Sunmax0731/blender-mcp/issues/148) hair preset と外部 add-on 方針

## 4. フェーズ

### Phase v2-0: docs 統合と Issue 分解

- `requirements`、`specification`、`design`、`roadmap`、`validation-plan` を canonical docs として統合する
- 進行単位を GitHub Issue に分解する

### Phase v2-1: template / schema 正式配置

- `blender_precision_config.yaml`
- `model_spec.yaml`
- `character_spec.yaml`
- `pipeline_spec.yaml`
- `validation_report`
- `addon_registry`
- これらの template / schema を正式配置し、docs と整合させる

### Phase v2-2: sidecar MCP server

- sidecar scaffold
- profile / tool pack / policy 読み込み
- `tools/list` による公開制御
- `blender_unavailable` 境界の明確化

### Phase v2-3: model spec / validation / visual QA

- scene / mesh / material validation
- visual QA artifact
- strict validation
- export manifest

### Phase v2-4: auto character foundations

- prompt 正規化
- 類型別 template / library
- live rig / shape key / weight bridge
- VRM / base asset 変換基盤

### Phase v2-5: pre-test 実装

- base asset pipeline 接続
- image reference 実装
- hair preset 実装
- auto-fix retry loop 実装

### Phase v2-6: test

- end-to-end dry-run test
- base asset あり / なしの live test
- image reference あり / なしの比較 test
- hair preset を含む live test
- retry traceability の確認

### Phase v2-7: release

- installer / docs / examples 更新
- validation evidence 整理
- release checklist 更新

## 5. pre-test backlog

テスト工程へ入る条件は次のとおり。

- pipeline が base asset あり / なしで分岐できる
- image input が `character_spec` と artifact に反映される
- hair preset が live build に反映される
- retryable failed に対して stage retry と traceability が残る

この条件を満たしたら、M5 の test track を次の単位へ分解する。

1. dry-run regression
2. live Blender regression
3. base asset reuse regression
4. image reference regression
5. hair preset regression
6. retry traceability regression
