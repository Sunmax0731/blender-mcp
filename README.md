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
- 工程の切り替わりごとに `docs/` と関連 Issue を見直し、差分を反映する
- 人が確認するドキュメント、Issue、コメント、PR 本文は日本語で記載する

ドキュメント:

- [要件定義](./docs/requirements.md)
- [設計](./docs/design.md)
- [仕様](./docs/specification.md)
- [ロードマップ](./docs/roadmap.md)
- [検証計画](./docs/validation-plan.md)
- [初回リリース計画](./docs/release-plan.md)
- [運用ルール](./AGENTS.md)
- [実行ガイド](./Skill.md)

想定する主要ユースケース:

- Codex から Blender に自然言語または構造化コマンドを送る
- Blender でモデリング補助やシーン操作を行う
- Blender 内 UI から Codex と対話する
- Blender と外部 AI サービスを接続する
- 生成結果や操作結果を Blender 上で確認、再編集する

## 開発環境

- OS: Windows
- Python: 3.11 系
- 依存管理: `uv`
- Blender: 5.1.1 で実機確認済み

## ローカルセットアップ

1. 依存を同期する

```powershell
uv sync --python 3.11 --extra dev
```

2. 自動テストを実行する

```powershell
uv run pytest
```

3. Blender UI スモークを実行する

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_blender_ui_smoke.ps1
```

## 現時点の検証結果

- `uv sync --python 3.11 --extra dev`: 成功
- `uv run pytest`: `16 passed`
- UI スモーク:
  - `controlled_launch`
  - `existing_process`
