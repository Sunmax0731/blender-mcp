# v2 release validation

v2 precision profile の release 前に、導入、sidecar MCP server、validation、visual QA、add-on integration、export、official examples の確認結果を追跡します。

## 1. Release Checklist

導入:

- `uv run blender-mcp-installer --plan` が公式 Blender MCP 導入 step を表示する
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender` が `precision-profile` step を表示する
- `scripts/install_precision_profile.ps1 -PlanConfigMerge` が `blender_precision` MCP server の追記予定を表示する
- GUI では precision profile を任意チェックボックスで導入できる
- 導入完了後に `Finish` で installer を閉じられる

sidecar MCP server:

- `uv run blender-precision-mcp --config templates/precision/blender_precision_config.yaml --profile precise --dry-run` が設定 summary を返す
- installer-managed venv から `scripts/start_precision_blender_mcp.ps1` で起動できる
- `execute_blender_code`、`run_unapproved_addon_operator`、`delete_all_objects_without_backup` は disabled tool として扱う

precision workflow:

- `model_spec.yaml` が schema validation に通る
- scene generation、validation、visual QA、mesh quality、export の artifact を保存できる
- destructive cleanup / operator は `dry_run -> confirm -> backup -> execute` を守る

## 2. Validation Commands

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
uv run python scripts\run_precision_workflow_smoke.py --output-dir artifacts\precision-workflow-smoke
```

```powershell
uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender
```

## 3. Official Example Smoke

### 3.1 Scene Analysis

手順:

1. Blender を起動し、解析対象の `.blend` を開く
2. 公式 `MCP` add-on が running であることを確認する
3. Codex App で `blender-official` MCP server が有効であることを確認する
4. 次の prompt を実行する

```text
現在開いている Blender scene を解析し、object 構成、material、light、camera、品質上の懸念、改善案を日本語でまとめてください。
```

合格条件:

- scene の object / material / camera / light に基づいた説明が返る
- 変更を伴わず analysis として完了する
- 重い mesh や整理候補がある場合、理由つきで説明される

### 3.2 Various Prompts

手順:

1. Blender を起動し、対象 `.blend` を開く
2. Codex App から複数の自然言語 prompt を実行する
3. 変更系 prompt は preview / confirm を挟む

prompt examples:

```text
現在の scene で、指定した material を使っている object を一覧化してください。
```

```text
Blenderで丸いキャラクターモデルを作成してください。body、arms、feet、eyes、mouth、cheeks、materials、lights、camera を設定し、最後に object 一覧と工夫点を説明してください。
```

合格条件:

- material / mesh / data-block などを自然言語で調査できる
- モデル作成 prompt では material、light、camera が作成される
- 必要に応じて review image または screenshot を確認できる

## 4. Integrated Precision Workflow Smoke

dry-run artifact 生成:

```powershell
uv run python scripts\run_precision_workflow_smoke.py --output-dir artifacts\precision-workflow-smoke
```

生成物:

- `scene_build_report.json`
- `validation_report.json`
- `review/review_manifest.json`
- `export_manifest.json`
- `prompt_samples.json`
- `smoke_summary.json`

live smoke は Blender 起動済み環境で実行し、実際の scene、review image、export file を確認します。

## 5. v2 Release 判断

v2 初期 Release は、次を満たす場合に候補とします。

- `uv run pytest` が成功している
- template / schema validation が成功している
- installer plan と precision profile config preview が実装と一致している
- official examples の手順が利用者向け docs にある
- integrated precision workflow smoke の artifact が生成できる
