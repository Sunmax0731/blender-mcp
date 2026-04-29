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
- reject 操作時の状態遷移
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

### 2.4 UI スモーク自動化
- add-on zip の再生成
- Blender add-on 配置先への同期
- ローカル MCP サーバーの起動確認
- Blender 未起動時の制御用インスタンス起動
- Blender 起動済み時の既存ウィンドウ前面化
- スクリーンショット保存
- モード別レポート保存

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
- `pytest` で 16 件成功
- `tests/test_mcp_roundtrip.py` で `/mcp` 経由の command round trip を確認
- `tests/test_request_status.py` で承認後結果の参照を確認
- `tests/test_ai_service.py` で AI 提案経路の成功系と未設定エラーを確認
- `tests/test_approval_operator.py` で reject 操作時の状態遷移と承認結果返却を確認

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

### 4.3 UI スモーク自動化確認
- 実行コマンド
  - `powershell -ExecutionPolicy Bypass -File .\scripts\run_blender_ui_smoke.ps1`
- 自動化対象
  - `build -> sync -> server health check -> Blender 起動または既存プロセス前面化 -> スクリーンショット保存`
- モード
  - `controlled_launch`
    - Blender 未起動時に制御用インスタンスを起動して撮影する
    - add-on 読込、サイドバー展開、UI レポート生成まで含めて再現性を担保する
  - `existing_process`
    - 可視ウィンドウを持つ既存 Blender を前面化して現在画面を撮影する
    - ユーザー作業中の状態を壊さないため、不要なクリックや `N` キー送信は行わない
- 現時点の確認済み証跡
  - `artifacts/blender-ui-smoke/20260429_230212/`
  - `artifacts/blender-ui-smoke/20260429_230244/`
- 備考
  - 起動直後の読込待ちを避けるため、撮影前待機は `-CaptureDelaySeconds` で調整する

### 4.4 手動確認として残す範囲
- Blender 画面上での日本語文言の見え方
- ボタン幅やレイアウトの最終確認
- reject 系操作時の操作感確認
- AI 提案文の妥当性確認

### 4.5 リリース準備として残す範囲
- セットアップ手順の最終見直し
- 既知制約の整理
- 配布物と検証証跡の対応付け

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

### 6.1 リリース判断に必要な証跡
- `pytest` の成功結果
- `/mcp` 経由 round trip の自動テスト結果
- Blender 実機シナリオの確認結果
- UI スモークのスクリーンショットとレポート
- 承認系の成功系と拒否系の確認結果
