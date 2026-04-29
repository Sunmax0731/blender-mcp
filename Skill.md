# Skill

このファイルは、`blender-mcp` を継続開発するために必要な作業スキルと標準手順を整理したものです。

## 1. 必要スキル

### 1.1 要件整理

- ユーザー要求を MVP と後続フェーズに分割する。
- 公式 Blender MCP の公開情報と、このリポジトリ独自要件を切り分ける。
- 判断が必要な項目を Issue に落とし込み、候補 3 案で整理する。

### 1.2 Blender Add-on 開発

- `bpy` によるオブジェクト操作
- `Panel` `Operator` `PropertyGroup` の実装
- Blender UI の状態表示、承認フロー、エラー表示の整備
- Blender 再読み込み、add-on 配布、バージョン更新の扱い

### 1.3 MCP Server 開発

- Python による MCP ツール公開
- Blender Add-on とのローカル通信設計
- ツール実行、承認待ち、結果返却、状態管理の実装
- Codex App から使いやすいインターフェース設計

### 1.4 Codex CLI 連携

- `codex exec` の非対話実行
- タイムアウト、失敗時メッセージ、fallback の実装
- Blender UI からのプロンプト送信を Codex CLI に橋渡しする設計

### 1.5 テストと検証

- `pytest` による自動テスト
- Blender 実機確認
- UI スモーク自動化
- Add-on 更新後の再読み込み確認

### 1.6 ドキュメント運用

- `docs/` と Issue コメントの同期
- 工程切替時の文書見直し
- 日本語文書の品質維持

## 2. 標準アーキテクチャ理解

### 2.1 Codex App 経路

- Codex App は MCP クライアントとして Blender を操作する。
- `Codex App -> MCP Server -> Blender Add-on -> Blender` を基本経路とする。

### 2.2 Blender プロンプト経路

- Blender UI からの自然言語入力は `Codex CLI` を使って解釈する。
- `Blender UI -> MCP Server -> Codex CLI -> 提案生成 -> Blender` を基本経路とする。

### 2.3 公式 Blender MCP との差分理解

- 公式 Blender MCP は Add-on と外部 MCP Server を別プロセスで構成する。
- 公式配布物は運用の参照元とし、このリポジトリでは Codex App / Codex CLI 向けの制御を追加する。
- 公式構成を無視して独自化しすぎないことを優先する。

## 3. 日常運用の標準手順

1. 要求を Issue 化する
2. 関連 Issue と `docs/` を確認する
3. 公式公開情報が関係するなら先に確認する
4. 実装する
5. テストする
6. Add-on を更新し、必要なら Blender を再読み込みする
7. Issue コメントへ結果を書く
8. 完了条件を満たしたら Issue をクローズする

## 4. 公式参照先

- Blender Lab: `https://www.blender.org/lab/mcp-server/`
- Releases: `https://projects.blender.org/lab/blender_mcp/releases`

参照時の確認ポイント:

- 必要 Blender バージョン
- Add-on と MCP Server の責務分離
- 配布物形式 `.zip` `.mcpb`
- LLM クライアントとの接続方式

## 5. ローカル開発コマンド

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

### 5.3 Add-on 更新

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

### 5.4 UI スモーク

```powershell
cd D:\Claude\MCP
powershell -ExecutionPolicy Bypass -File .\scripts\run_blender_ui_smoke.ps1
```

## 6. 判断基準

### 6.1 実装方針

- 公式構成に寄せられるなら寄せる
- ローカル完結で運用できる方を優先する
- 人手確認を減らせるなら自動化を優先する

### 6.2 AI 経路

- Blender UI からの提案生成は `Codex CLI` 優先
- 外部 API 依存はできるだけ減らす
- 返答が不適切ならローカル fallback を使う

### 6.3 ドキュメント

- 人が見るものは日本語
- Issue だけでなく `docs/` にも残す
- 文字化けした文書は放置せず修正する
