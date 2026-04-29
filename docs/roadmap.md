# ロードマップ

## Phase 0: 立ち上げ
- 要件、仕様、設計、検証計画の整理
- GitHub リポジトリ準備
- 初期 Issue 作成

## Phase 1: 接続確認 MVP
- Blender add-on 最小構成
- MCP サーバー最小構成
- `status` `create_primitive` `list_objects` `transform_object` `delete_object(confirm)` の実装
- Blender UI に接続状態、チャット履歴、タブ UI、ログ表示を追加
- Blender add-on 主導の常時接続と疎通確認

## Phase 2: 対話 UI と承認フロー
- Blender UI から Codex と連携できる導線を整備
- 承認待ちフロー実装
- 監査ログ実装
- 最小運用 UI と状態表示の整備

## Phase 3: AI サービス連携
- OpenAI 互換 API 連携
- 提案生成の初期実装
- プロンプトとシーン情報連携

## Phase 4: 検証とリリース準備
- エラー処理強化
- テスト拡充
- UI スモーク自動化の運用
- reject 系を含む手動確認
- 初回リリース計画の整備
- リリース

## 優先順
1. 接続と操作の最小実装
2. Blender UI の可視化と承認導線
3. AI 連携
4. 検証強化
