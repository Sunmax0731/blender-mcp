# v2 release validation

v2 precision profile の release 前に、導入、sidecar MCP server、validation、visual QA、add-on integration、examples の確認結果を追跡する。

## 1. Release Checklist

### 1.1 導入

- `uv run blender-mcp-installer --plan` が公式 Blender MCP 導入 step を表示する
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender` が `precision-profile` step を表示する
- `scripts/install_precision_profile.ps1` が Codex home 配下へ precision profile、Skill、subagent template をコピーする
- GUI では precision profile を任意チェックボックスで導入できる
- 導入完了後に Finish 操作で installer を閉じられる

### 1.2 sidecar MCP server

- `uv run blender-precision-mcp --config templates/precision/blender_precision_config.yaml --profile precise --dry-run` が設定 summary を返す
- profile / tool-pack によって公開 tool が切り替わる
- `execute_blender_code`、`run_unapproved_addon_operator`、`delete_all_objects_without_backup` は既定で block される
- control tool と profile tool の区別が docs と一致している

### 1.3 model spec / validation

- `templates/precision/model_spec.yaml` が schema validation に通る
- `validate_scene_against_spec` が `validation_report` 形式の structured result を返す
- 失敗時は `failures[].suggestion` を含む
- report artifact を保存できる
- `live_scene=true` の場合、Blender live scene の object / material / camera / light 実測値を report に含める
- Blender 外実行では `live_scene.available=false` と `error.code=BLENDER_NOT_AVAILABLE` を返す

### 1.4 visual QA

- `scripts/capture_precision_review_views.py --dry-run` が review manifest を保存する
- Blender Python 内では front / side / top / perspective の screenshot を保存できる
- manifest は `views`、`resolution`、`artifacts`、`warnings` を含む
- manifest は `target_objects`、`captures`、`quality_checks`、`errors` を含む
- blank check / bounding box check が failed の場合、`status=failed` になる
- Blender 未起動、対象 object 不在、未対応 view は `errors[].code` で区別する

### 1.5 add-on integration

- `templates/precision/addon_registry.yaml` が schema validation に通る
- `scripts/inspect_precision_addons.py --mode capabilities` が approved operator metadata を返す
- registry にない operator は execution wrapper で拒否される
- destructive operator は `backup_required` を要求する
- destructive operator は `confirm=true` なしでは `confirmation_required` を返す
- `backup_required=true` の operator は実行前に target / active object を duplicate し、backup object 名を result に残す
- Blender Python がない環境では structured failure を返す

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
uv run python scripts\capture_precision_review_views.py --spec templates\precision\model_spec.yaml --output-dir tmp\precision-review-dryrun --views front,top --dry-run
```

```powershell
uv run python scripts\inspect_precision_addons.py --mode capabilities --module example_retopology_addon
```

```powershell
uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender
```

## 3. Issue #90 Live Scene Validation Smoke

`validate_scene_against_spec` は `live_scene=true` を指定すると、Blender live scene の実測値を `validation_report` に含める。

確認項目:

- Blender 外で実行した場合は `live_scene.available=false` と `error.code=BLENDER_NOT_AVAILABLE` を返す
- Blender live scene で実行した場合は object / material / active camera / lights を取得する
- 公式 Blender MCP で取得した snapshot を `live_scene_snapshot` として渡せる
- `model_spec.yaml` の `dimensions` と `location` は threshold と照合され、根拠値を `checks[].evidence` または `failures[].evidence` に残す
- `require_camera` / `require_lights` は live scene の実体で判定する

最小 smoke:

```powershell
uv run pytest tests\test_precision_validation.py
```

Blender 外で structured error を確認する例:

```powershell
uv run python -c "from blender_precision_mcp.validation import validate_model_spec; import json; print(json.dumps(validate_model_spec('templates/precision/model_spec.yaml', live_scene=True), ensure_ascii=False, indent=2))"
```

## 4. Issue #91 Visual QA Smoke

`capture_review_views` は review image を保存し、`review_manifest.json` に撮影条件と画像 QA の結果を記録する。

確認項目:

- dry-run では image を保存せず、予定される `captures[]` と `artifacts[]` を manifest に残す
- 実 capture では Blender scene から指定 view の PNG を保存する
- `quality_checks[]` に `blank_check` と `bounding_box_check` を記録する
- unsupported view は `errors[].code=VIEW_NOT_SUPPORTED` として返す
- Blender Python が使えない場合は `errors[].code=BLENDER_NOT_AVAILABLE` として返す
- spec に定義された object が scene にない場合は `errors[].code=TARGET_OBJECT_NOT_FOUND` として返す

最小 smoke:

```powershell
uv run pytest tests\test_precision_visual_qa.py
uv run python scripts\capture_precision_review_views.py --dry-run --views front,top --output-dir outputs\reviews\dry-run
```

実 screenshot は Blender Python または公式 Blender MCP から Blender 側の render / screenshot API を実行し、生成された PNG を `analyze_review_image` で確認する。

## 5. Issue #92 Approved Operator Live Integration Smoke

approved add-on operator は `preview -> confirm -> execute` と backup を必須条件として扱う。

確認項目:

- `dry_run=true` は operator、mapped parameter、context、`safety_actions` を返す
- destructive operator は `confirm=true` なしでは `confirmation_required` を返す
- `backup_required=true` の operator は実行前に target object または active object を duplicate する
- operator 実行結果、backup object 名、context error を structured result に残す
- Blender 内 Python で registry JSON を使った representative operator smoke が通る

最小 smoke:

```powershell
uv run pytest tests\test_precision_operator_execution.py
uv run python scripts\inspect_precision_addons.py --mode operators
```

live smoke では公式 Blender MCP から一時 operator `object.codex_smoke_backup` を登録し、次を確認した。

- preview: `success=true`
- confirm なし execute: `confirmation_required`
- confirm あり execute: `success=true`
- backup: `CodexSmokeTarget_backup_before_object_codex_smoke_backup`
- result: `FINISHED`

## 6. Examples

### 6.1 Scene Analysis

目的: Blender scene を確認し、現在の構成、検証結果、改善点を把握する。

利用者向け手順:

1. Blender を起動し、公式 `MCP` add-on を有効にする
2. Codex App を起動し、`blender-official` を利用できる状態にする
3. 次のように依頼する

```text
現在の Blender シーンを分析し、オブジェクト構成、材質、ライト、カメラ、品質上の問題、修正案を日本語でまとめてください。
```

v2 precision profile では、必要に応じて `get_scene_snapshot`、`validate_scene_against_spec`、`capture_review_views` を使い、validation report と review artifact を残す。

### 6.2 Various Prompts

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

## 7. Known Limitations

- v2 sidecar の一部 tool は公開制御と structured `not_implemented` までの初期実装である
- visual QA の実 screenshot 保存は Blender Python または公式 Blender MCP から Blender render / screenshot API を実行する必要がある
- visual QA の自動判定は blank / bounding box の最低限チェックであり、意味的な見た目評価は人の review が必要である
- 実 add-on operator の live 実行は Blender Python と対象 add-on が導入済みの環境で検証する必要がある
- 現時点の live smoke は一時登録 operator による統合経路確認であり、外部 retopology add-on 固有の品質評価は別途必要である
- precision profile installer は Codex home へ template / Skill / subagent をコピーする。v1 系では `blender_precision` MCP server の自動登録は行わない

## 8. v2 初期 Release 判断

v2 初期 Release は、以下を満たす場合に候補とする。

- `uv run pytest` が成功している
- template / schema validation が成功している
- installer plan に precision profile step が表示される
- known limitations が release docs に明記されている
