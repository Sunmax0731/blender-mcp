# AGENTS

`blender-mcp` は、公式 Blender MCP をベースに Codex 連携を整備するためのリポジトリです。

## 1. 基本ルール

- すべての変更は GitHub Issue を起点に進める
- ドキュメント更新だけの依頼でも Issue 化してから着手する
- 人が確認する成果物は日本語で記載する
- 1 つの Issue を完了させてから次へ進む
- 判断が必要な項目は Issue に候補 3 案、判断基準、判断材料、推奨案を書く
- ユーザーの判断や決定が必要な Issue では、決定依頼だけで終わらせず、判断材料つきで候補案を提示する
- 候補案には最低限、各案の長所、短所、影響範囲を書き、最後に推奨案と推奨理由を書く

## 2. 工程順序

1. 要件定義
2. 仕様検討
3. 設計
4. 実装
5. テスト
6. リリース

工程切替時は関連 Issue と `docs/` を見直し、変更理由を Issue コメントへ残す。

## 2.1 判断が必要な Issue の書式

- タイトルと本文だけでなく、Issue 内に `判断が必要な項目` を明記する
- 各判断項目には候補 3 案を基本とし、案ごとの比較材料を添える
- 比較材料には、目的適合性、実装コスト、運用コスト、リスク、既存資産の再利用可否を含める
- 最後に `推奨案` と `推奨理由` を書き、ユーザーがそのまま判断できる状態にする

## 3. 見直し対象ドキュメント

- `README.md`
- `docs/requirements.md`
- `docs/specification.md`
- `docs/design.md`
- `docs/roadmap.md`
- `docs/validation-plan.md`
- 必要に応じて `docs/release-plan.md`

## 4. 技術方針

### 4.1 公式優先

- Blender 側の中核機能は公式 `blender_mcp` を使う
- 独自実装は公式で不足する部分だけに限定する
- 既存独自 add-on / server は段階的に縮退する

### 4.2 接続経路

- `Codex App -> 公式 MCP server -> 公式 Blender add-on -> Blender`
- `Blender UI -> 補助ブリッジ -> Codex CLI -> 公式 Blender MCP / Blender`

### 4.3 安全方針

- 危険操作は `preview -> confirm -> execute`
- 任意 Python 実行や無制限 `bpy` 実行はデフォルトで許可しない
- ローカル実行を前提とし、外部公開前提の構成にしない

## 5. 標準コマンド

### 5.1 依存同期

```powershell
cd D:\Claude\MCP
uv sync --python 3.11 --extra dev
```

### 5.2 テスト

```powershell
cd D:\Claude\MCP
uv run pytest
```

### 5.3 公式 add-on 導入

```powershell
cd D:\Claude\MCP
.\scripts\install_official_blender_mcp.ps1
```

### 5.4 既存自動化

現時点の自動化スクリプトは独自実装前提のものを含む。今後は公式構成へ寄せて整理する。
