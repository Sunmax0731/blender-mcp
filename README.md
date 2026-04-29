# blender-mcp

Codex から Blender を操作し、Blender 内 UI と外部 AI サービス連携を含む MCP ベースの開発基盤を構築するプロジェクトです。

このリポジトリでは、通常のシステム開発と同様に以下の順序で進めます。

1. 要件定義
2. 仕様検討
3. 設計
4. 実装
5. テスト
6. リリース

運用方針:

- GitHub でプロジェクトを管理する
- Issue 駆動で 1 件ずつ進める
- 要件/設計/仕様は `docs/` を正とする
- 実装開始前に対象 Issue の受け入れ条件を明確化する

ドキュメント:

- [要件定義](./docs/requirements.md)
- [設計](./docs/design.md)
- [仕様](./docs/specification.md)
- [ロードマップ](./docs/roadmap.md)
- [検証計画](./docs/validation-plan.md)

想定する主要ユースケース:

- Codex から Blender に自然言語または構造化コマンドを送る
- Blender でモデリング補助やシーン操作を行う
- Blender 内 UI から Codex と対話する
- Blender と外部 AI サービスを接続する
- 生成結果や操作結果を Blender 上で確認、再編集する
