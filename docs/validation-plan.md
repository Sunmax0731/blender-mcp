# 検証計画

## 1. 検証方針

- 実装と同時に手動検証と自動検証の両方を整備する
- Blender 実機確認を必須とする
- 破壊的操作は専用テストケースで扱う
- 承認待ち操作は「承認待ち表示」と「承認後実行結果」を分けて確認する

## 2. テストレベル

### 2.1 単体テスト

- リクエスト検証
- 構造化操作変換
- コマンドキュー
- 承認待ち判定
- 承認済み実行ロジック
- AI プロバイダアダプタ
- ログ/監査フォーマット

### 2.2 結合テスト

- MCP サーバーと Blender アドオン接続
- `/mcp` 経由の tool 一覧取得
- `blender_status` 呼び出し
- add-on 向け `/api/addon/status` `/api/addon/command/poll` `/api/addon/command-result`
- Blender UI からの送信
- MCP ツール経由の実行

### 2.3 手動シナリオ

- Blender 起動中/未起動時の状態確認
- Cube 作成、移動、一覧取得
- 承認付き削除の確認
- 承認待ち表示の確認
- 承認実行後の Blender シーン更新確認
- AI 提案の取得と却下/採用

## 3. 受け入れテスト

### Phase 1

- 接続、作成、変形、一覧取得が安定動作
- `blender_status` が未接続状態を正しく返す
- `blender_create_primitive` `blender_list_objects` `blender_transform_object` が呼び出せる

### Phase 2

- UI から接続状態、履歴、結果、承認待ちを確認できる
- `Execute Approved Action` と `Reject Action` が UI 上で動作する
- 承認待ち request id を UI で追跡できる

### Phase 3

- AI 提案を安全に利用できる
- OpenAI 互換 API 連携で提案取得まで確認できる

## 4. 承認フロー検証観点

### 4.1 現在の MVP 観点

- delete 要求で `executionMode=confirm_required` が返る
- Blender UI に pending action と request id が表示される
- UI から承認実行できる
- UI から reject できる

### 4.2 別 Issue で追う観点

- 承認後の最終結果を Codex 側で一貫して追跡できること
- 承認待ち request を跨いだ再通知フロー
- 監査ログとの突合

## 5. 検証環境

- Windows 開発環境
- Blender LTS
- `uv` 管理の Python 3.11 仮想環境

## 6. リリース判定

- P0/P1 不具合が解消済み
- 主要ユースケースが通る
- セットアップ手順が再現可能
- 既知制約が README または docs に明記されている
- 承認フローの既知制約が Issue と docs に反映されている
