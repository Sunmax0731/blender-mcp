# ロードマップ

## Phase 0: 公式構成への切替

- 公式 Blender MCP の調査
- docs の公式前提化
- 移行方針 Issue の整備

## Phase 1: 公式 add-on 導入基盤

- 公式 add-on の取得
- Blender への導入
- Windows 用導入スクリプト整備

## Phase 2: Codex App 利用経路

- `blender-official` の登録
- 利用手順の明文化
- Codex App からの接続確認

## Phase 3: 既存構成の cleanup

- 旧補助 UI 登録の cleanup
- 利用者向け導線の一本化

## Phase 4: 更新と検証の自動化

- 再導入と再検証の整備
- ログと証跡の整理

## Phase 5: 1クリック導入アプリ

- GUI 実装
- `exe` 化
- 第三者 plugin 自動導入
- 補助 add-on 自動導入
- release asset 化

## Phase 6: 外部 3D サービス連携

- External Services 共通設定
- provider 層
- plugin bridge helper
- 3D View パネル
- experimental release

## 2026年5月1日時点の現在地

- 公式 Blender MCP 導入基盤: 完了
- 第三者 plugin 自動導入: 完了
- 補助 add-on 自動導入: 完了
- External Services 共通 UI: 完了
- Meshy / Tripo / Rodin の plugin bridge 手動確認: 完了
- SPAR3D の provider 骨格: 完了
- API キー前提の実サービス確認: 未完了

## `v1.2.0` の位置づけ

`v1.2.0` は、次を含む experimental release とする。

- 外部 3D サービス連携の補助 UI
- 第三者 plugin 自動導入
- 補助 add-on 自動導入
- `plugin_bridge` 状態確認

## 次の優先課題

1. API キー入手後の Meshy / Tripo / Rodin / SPAR3D 実サービス検証
2. SPAR3D の API 契約固定
3. Poly Haven の UI 再開条件整理
4. release asset 生成の更なる自動化
