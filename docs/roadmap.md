# ロードマップ

## Phase 0: 公式構成への切替

- 公式 Blender MCP の調査
- docs を公式前提へ更新
- 移行方針 Issue の整備

## Phase 1: 公式 add-on 導入基盤

- 公式 `mcp-1.0.0.zip` の取得
- Blender add-on 配置先への同期
- Windows 用導入スクリプト整備

## Phase 2: Codex App 利用経路

- Codex App から公式 MCP を使う前提整理
- 利用手順と必要設定の明文化
- 実行経路の検証

## Phase 3: 導入環境の整理

- 旧 `blender_mcp` add-on 登録の cleanup を installer に組み込む
- 利用者向け導線を Codex App と公式 MCP に一本化する

## Phase 4: 更新と検証の自動化

- 公式版更新検知
- 再導入・再検証自動化
- スクリーンショットとログの証跡化

## Phase 5: 1クリック導入アプリ

- 要件確定
- 仕様と設計の整理
- GUI 実装と `exe` 化
- 導入後の live 接続確認
- Release 資産化

## 直近優先

1. 公式 MCP 導線と旧開発版 add-on 登録 cleanup の安定化
2. precision profile 導入直後の正常系と `blender_unavailable` 切り分けの docs 整備
3. 高品質モデル制作向け Skill / Agent 指示の整備
4. 公式 Blender MCP Example の利用者向け掲載

## v2: 精密モデリング完成ロードマップ

v2 の詳細な完成ロードマップは [v2 精密モデリング完成ロードマップ](v2-precision-roadmap.md) に分離する。既存 Phase 0-5 は公式 Blender MCP 導入と MVP 配布の流れとして維持し、v2 はその上に高品質モデリング、検証、add-on integration、Skill / subagent 配布を追加する。

直近の v2 優先順:

1. v2 資料を canonical docs と Issue 群へ統合する
2. template / schema / config を正式配置する
3. sidecar MCP server の scaffold と profile / tool-pack 制御を実装する
4. model spec、validation report、visual QA を実装する
5. add-on registry と approved operator 実行を実装する

## 新規トラック: 全自動キャラクターモデル生成

5 要件完全自動を目指す新規トラックは、工程ごとに次の milestone で進める。

1. M1: 全自動キャラクターモデル生成 要件定義
2. M2: 全自動キャラクターモデル生成 仕様検討
3. M3: 全自動キャラクターモデル生成 設計
4. M4: 全自動キャラクターモデル生成 実装
5. M5: 全自動キャラクターモデル生成 テスト
6. M6: 全自動キャラクターモデル生成 リリース

M1 では、形状、材質、ボーン、シェイプキー、ウェイト、prompt 駆動オーケストレーションの 6 Issue に分解して要件定義を開始する。

## 現在地

2026-04-30 時点の進捗は次のとおり。

- M1 要件定義: 完了
- M2 仕様検討: 完了
- M3 設計: 完了
- M4 実装: 進行中
- M5 テスト: 未着手
- M6 リリース: 未着手

M4 で実装済みの主な範囲:

- `character_spec` / `pipeline_spec` の正規化
- 類型別 template / library
- dry-run workflow と validator 骨格
- live scene build と strict validation
- live rig / shape key / weight bridge
- `BaseAvatar.vrm -> BaseAvatar.blend` 変換
- `.blend` から `base_asset_manifest.json` / `adaptation_plan.json` 生成

## テスト工程前に必要な実装

M5 へ入る前に必要な実装タスクは次のとおり。

1. [#151](https://github.com/Sunmax0731/blender-mcp/issues/151) base asset manifest を auto character pipeline に接続する
2. [#153](https://github.com/Sunmax0731/blender-mcp/issues/153) 画像入力から `character_spec` 補強と `image_reference_manifest` を生成する
3. [#154](https://github.com/Sunmax0731/blender-mcp/issues/154) hair preset library と live hair build を追加する
4. [#155](https://github.com/Sunmax0731/blender-mcp/issues/155) auto-fix retry loop と stage retry traceability を追加する

実装判断の残件:

- [#148](https://github.com/Sunmax0731/blender-mcp/issues/148) hair preset と外部 add-on 方針

## テスト工程の入口条件

次を満たしたら M5 テストへ進む。

- base asset あり / なしの両経路で pipeline を分岐できる
- image input を `character_spec` と artifact に反映できる
- hair preset を live build に反映できる
- retryable failed に対して stage retry と traceability を残せる
