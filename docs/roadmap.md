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
