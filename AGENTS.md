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
- GitHub Issue / comment に日本語本文を投稿するときは、PowerShell のパイプで `gh ... --body-file -` へ直接流さない
- 日本語本文は必ず UTF-8 で保存した一時ファイルを `--body-file <path>` で渡す
- Issue / comment 投稿前に、PowerShell の `$OutputEncoding` と code page に依存した文字化け経路を避ける
- GitHub の日本語更新は「新規投稿」だけでなく「Issue 本文更新」「コメント更新」でも同じ文字化け対策を適用する
- `gh issue edit --body-file <path>`、`gh issue comment --body-file <path>`、必要なら `gh api ... --input <json>` を使い、PowerShell の埋め込み文字列で直接更新しない
- パスに `\` を含む本文やコードブロックは文字化けや制御文字混入を招きやすいため、Issue 本文では `/` 区切りを優先する
- GitHub 更新後は `gh issue view` または GitHub 画面で本文とコメントの両方を確認し、崩れていたらその場で API 経由で修正する
- open Issue を進める前に、その Issue でユーザー判断が必要かを必ず点検する
- ユーザー判断が必要な項目を見つけたら、実装を進め切る前に Issue コメントとユーザー向け回答の両方で候補案、判断基準、判断材料、推奨案を提示する

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
- まだ判断項目が本文にない既存 open Issue でも、着手時点で必要ならコメントで同じ形式を補う

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

### 4.4 モデリング品質方針

- Blender MCP でモデルを作る場合は、生成物を専用コレクションに分ける
- 体、部品、装飾、ライト、カメラ、検証用レンダーを分けて考える
- オブジェクト名とマテリアル名は、人が Outliner と Material Properties で理解できる名前にする
- 完了前に、カメラから見えること、マテリアルが割り当たっていること、確認画像が空や過度な切り抜きでないことを確認する
- 利用者配布用の品質指示は `skills/blender-quality-modeling/` に置き、詳細な利用手順は `docs/skills.md` に記載する

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

### 5.5 GitHub 投稿時の文字化け防止

```powershell
$bodyPath = Join-Path $env:TEMP 'gh-issue-body.md'
[System.IO.File]::WriteAllText($bodyPath, $bodyText, [System.Text.UTF8Encoding]::new($false))
gh issue create --title '<title>' --body-file $bodyPath
```

- `@' ... '@ | gh issue create --body-file -` のようなパイプ経路は使わない
- コメント投稿や Issue 更新でも同じく UTF-8 ファイル経由に統一する
- コメント更新は `gh api repos/<owner>/<repo>/issues/comments/<id> --method PATCH --input <json>` を優先する
- 更新後確認で文字化けを見つけたら、崩れた本文を再利用せず、正しい UTF-8 ソースを作り直して再投稿する
