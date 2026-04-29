# AGENTS

このファイルは、`blender-mcp` リポジトリで作業する際の共通運用ルールを定義する。

## 1. 基本方針

- すべての作業は GitHub Issue を起点に進める。
- ドキュメント更新だけの依頼でも、着手前に Issue 化する。
- 人が読む成果物は `README.md`、`docs/`、Issue、Issue コメントを含めて日本語で記載する。
- 1 つの Issue を完了させてから次の Issue に進む。
- 判断が必要な項目は Issue に候補 3 案、判断基準、判断材料、推奨案を残す。

## 2. 工程順序

以下の順序で進める。

1. 要件定義
2. 仕様検討
3. 設計
4. 実装
5. テスト
6. リリース

工程を切り替えるときは、関連 Issue とドキュメントを見直してから次工程へ進む。

## 3. 工程切替時の必須見直し

工程の切替時は、最低限以下を確認・更新する。

- `docs/requirements.md`
- `docs/specification.md`
- `docs/design.md`
- `docs/roadmap.md`
- `docs/validation-plan.md`
- 必要に応じて `docs/release-plan.md`

更新理由は関連 Issue に記録する。

## 4. Blender MCP の標準構成方針

このリポジトリでは、公式 Blender MCP の公開情報を参照しつつ、以下の 2 系統を両立する。

### 4.1 Codex App から Blender を操作する経路

- `Codex App -> MCP Server -> Blender Add-on -> Blender`
- Codex App 側からは MCP ツールとして Blender を操作できる構成を維持する。
- この経路は、対話 UI ではなく MCP ツール経由で明示的に Blender を操作したい場合の主経路とする。

### 4.2 Blender UI からプロンプトを送る経路

- `Blender UI -> ローカル MCP Server -> Codex CLI -> 提案生成 -> Blender`
- Blender 内のプロンプト送信は、外部 API ではなく `Codex CLI` をバックグラウンド実行する構成を優先する。
- API キー依存を避け、ローカル PC 上で完結する提案経路を標準とする。

## 5. 公式 Blender MCP の扱い

公式情報は以下を正本の参照元とする。

- Blender Lab: `https://www.blender.org/lab/mcp-server/`
- Releases: `https://projects.blender.org/lab/blender_mcp/releases`

公式公開情報から読み取る前提は以下。

- Blender 5.1 以降を前提とする。
- Blender Add-on と外部 MCP Server は別プロセスで動作する。
- Blender Add-on と MCP Server の橋渡しはローカル通信で行う。
- LLM クライアント側は差し替え可能である。

このリポジトリでは、公式構成を参照しつつ、Codex App と Codex CLI に最適化したローカル運用を実装する。

## 6. 実装上のルール

- Blender 側の実処理は `bpy` を通じて行う。
- 破壊的操作は `preview -> confirm -> execute` を基本とする。
- AI 提案は補助であり、無制限な任意 Python 実行は許可しない。
- Allowlist に含める操作だけを自動実行対象とする。
- Codex CLI の返答が曖昧、英語のみ、または依頼と無関係な場合はローカル fallback を使う。

## 7. 更新・検証の標準手順

### 7.1 依存同期

```powershell
cd D:\Claude\MCP
uv sync --python 3.11 --extra dev
```

### 7.2 テスト

```powershell
cd D:\Claude\MCP
uv run pytest
```

### 7.3 Add-on 更新とサーバー再起動

PowerShell:

```powershell
cd D:\Claude\MCP
.\scripts\update_blender_addon.ps1
```

コマンドプロンプト:

```bat
cd /d D:\Claude\MCP
scripts\update_blender_addon.cmd
```

### 7.4 UI スモーク確認

```powershell
cd D:\Claude\MCP
powershell -ExecutionPolicy Bypass -File .\scripts\run_blender_ui_smoke.ps1
```

## 8. Issue への反映ルール

- 実装した内容
- 判断理由
- 実行したテスト
- 手動確認の結果
- 残課題や follow-up

これらを Issue コメントへ残し、完了条件を満たしたら Issue をクローズする。
