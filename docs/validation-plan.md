# 検証計画

## 1. 目的
- 実装内容が仕様どおりに動作することを確認する
- Blender 実機とローカル MCP サーバーの往復を確認する
- 承認待ち操作と承認後操作の整合を確認する
- AI 提案経路の成功系と失敗系を確認する

## 2. テストレベル

### 2.1 単体テスト
- リクエスト検証
- ステータス管理
- コマンドキュー
- コマンド実行ロジック
- 承認結果保持
- AI プロバイダアダプタ
- ログとエラー整形

### 2.2 結合テスト
- MCP サーバーと Blender add-on 間の HTTP 通信
- `/mcp` 経由の tool 一覧取得
- `blender_status` 応答確認
- add-on 側 `status` `command/poll` `command-result` `approval-result` の往復
- Blender UI 状態遷移との整合
- 承認後結果の後続参照

### 2.3 実機シナリオ
- Blender 起動中と未起動時の接続状態確認
- Cube 作成、移動、一覧取得
- 削除要求時の `confirm_required` 応答確認
- 承認実行後の結果確認
- 承認拒否時の結果確認
- Blender シーン反映確認
- AI 提案取得と画面上の履歴反映確認

## 3. フェーズ別テスト

### Phase 1
- 接続、状態取得、作成、一覧取得、変形が成功する
- `blender_status` が接続状態を正しく返す
- `blender_create_primitive` `blender_list_objects` `blender_transform_object` が往復する

### Phase 2
- UI から接続確認、履歴表示、承認待ち、承認実行ができる
- `Execute Approved Action` と `Reject Action` が機能する
- request id を UI 上で追跡できる

### Phase 3
- AI 提案要求を送信できる
- OpenAI 互換 API 連携で提案本文を取得できる
- API 未設定、タイムアウト、接続失敗、HTTP エラーを区別できる

## 4. 現時点の確認結果

### 4.1 自動テスト
- `pytest` で 15 件成功
- `tests/test_mcp_roundtrip.py` で `/mcp` 経由の command round trip を確認
- `tests/test_request_status.py` で承認後結果の参照を確認
- `tests/test_ai_service.py` で AI 提案経路の成功系と未設定エラーを確認

### 4.2 Blender 実機確認
- 実行環境: `Blender 5.1.1`
- add-on の `register()` / `unregister()` を実行確認済み
- 実機シナリオで以下を確認済み
  - `Connect`
  - `Send Prompt`
  - `blender_create_primitive`
  - `blender_list_objects`
  - `blender_delete_object` の `confirm_required`
  - 承認実行後の `approved_executed`

### 4.3 残タスク
- Blender 画面上でのパネル表示、文言、レイアウト確認
- 拒否系の実機確認
- リリース向けの手順書整備

## 5. 検証環境
- Windows ローカル環境
- Blender 実機
- `uv` 管理の Python 3.11 系
- ローカル HTTP 接続
- 必要に応じて OpenAI 互換 stub サーバー

## 6. 完了条件
- P0/P1 の主要経路が自動または実機で確認済み
- 人向けドキュメントが最新状態に更新されている
- 既知の制約と残課題が Issue に記録されている
- リリース判断に必要な証跡が揃っている
