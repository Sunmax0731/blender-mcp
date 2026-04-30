# v2 release validation

## 1. 目的

v2 precision profile の release 前に、導入、sidecar MCP server、validation、visual QA、add-on integration、Blender UI prompt flow、examples の確認結果を 1 箇所で追跡する。

## 2. Release checklist

### 2.1 導入

- `uv run blender-mcp-installer --plan` が公式 Blender MCP 導入ステップを表示する
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender` が `precision-profile` ステップを表示する
- `scripts/install_precision_profile.ps1` が Codex home 配下へ precision profile、Skill、subagent template をコピーする
- GUI では precision profile が任意チェックボックスで導入できる
- 導入完了後に Finish 操作で installer を閉じられる

### 2.2 sidecar MCP server

- `uv run blender-precision-mcp --config templates/precision/blender_precision_config.yaml --profile precise --dry-run` が設定 summary を返す
- profile / tool-pack によって公開 tool が切り替わる
- `execute_blender_code`、`run_unapproved_addon_operator`、`delete_all_objects_without_backup` は既定で block される
- control tool と profile tool の区別が docs と一致している

### 2.3 model spec / validation

- `templates/precision/model_spec.yaml` が schema validation に通る
- `validate_scene_against_spec` が `validation_report` 形式の structured result を返す
- 失敗時は `failures[].suggestion` を含める
- report artifact を保存できる

### 2.4 visual QA

- `scripts/capture_precision_review_views.py --dry-run` が review manifest を保存する
- Blender Python 内では front / side / top / perspective の screenshot を保存できる
- manifest は `views`、`resolution`、`artifacts`、`warnings` を含む

### 2.5 add-on integration

- `templates/precision/addon_registry.yaml` が schema validation に通る
- `scripts/inspect_precision_addons.py --mode capabilities` が approved operator metadata を返す
- registry にない operator は execution wrapper で拒否される
- destructive operator は `backup_required` を要求する
- Blender Python がない環境では structured failure を返す

### 2.6 Blender UI prompt flow

- Sidebar に `Plan`、`Confirm`、`Execute` が表示される
- `Plan` は提案と Preview を作成し、即時実行しない
- `Confirm` なしの `Execute` は実行されない
- 旧 `send_prompt` operator は互換用に維持される

## 3. Validation commands

```powershell
uv run pytest
```

```powershell
uv run --with pyyaml --with jsonschema python scripts\validate_precision_templates.py
```

```powershell
uv run blender-precision-mcp --config templates\precision\blender_precision_config.yaml --profile precise --tool-pack validation,visual_qa --dry-run
```

```powershell
uv run python scripts\capture_precision_review_views.py --spec templates\precision\model_spec.yaml --output-dir tmp\precision-review-dryrun --views front,top --dry-run
```

```powershell
uv run python scripts\inspect_precision_addons.py --mode capabilities --module example_retopology_addon
```

```powershell
uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender
```

## 4. Examples

### 4.1 Scene Analysis

目的: Blender scene を確認し、現在の構成、検証結果、改善点を把握する。

利用者向け手順:

1. Blender を起動し、公式 `MCP` add-on を有効にする
2. Codex App を再起動し、`blender-official` または `blender_precision` MCP server を利用できる状態にする
3. 次のように依頼する

```text
現在の Blender シーンを分析し、オブジェクト構成、材質、ライト、カメラ、品質上の問題、修正案を日本語でまとめてください。
```

v2 precision profile では、必要に応じて `get_scene_snapshot`、`validate_scene_against_spec`、`capture_review_views` を使い、validation report と review artifact を残す。

### 4.2 Various Prompts

目的: 利用者が自然言語で複数種類のモデリング依頼を試せるようにする。

例:

```text
丸みのある小型ロボットを作成してください。部品名、マテリアル、ライト、カメラ、確認画像も設定してください。
```

```text
現在のモデルを検証し、寸法、命名、材質、メッシュ品質、レビュー画像の不足を report にしてください。
```

```text
approved add-on registry を確認し、利用可能な retopology operator と実行前に必要な context を説明してください。
```

## 5. Known limitations

- v2 sidecar の一部 tool は、公開制御と structured `not_implemented` までの初期実装である
- Blender live scene の実測値差分 validation は、schema / static validation の上に追加する余地がある
- visual QA の実 screenshot 保存は Blender Python 内で実行する必要がある
- add-on operator の実実行は Blender Python と対象 add-on が導入済みの環境で検証する必要がある
- precision profile installer は Codex home へ template / Skill / subagent をコピーする。既存 `config.toml` への自動マージはまだ行わない

## 6. v2 初期 release 判定

v2 初期 release は、以下を満たす場合に候補とする。

- #62 から #72 が完了している
- `uv run pytest` が成功している
- template / schema validation が成功している
- installer plan に precision profile step が表示される
- known limitations が release docs に明記されている
