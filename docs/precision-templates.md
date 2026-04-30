# v2 precision template / schema

v2 precision modeling で利用する template と schema をまとめたドキュメントです。

## 配置

template:

- [`templates/precision/blender_precision_config.yaml`](../templates/precision/blender_precision_config.yaml)
- [`templates/precision/model_spec.yaml`](../templates/precision/model_spec.yaml)
- [`templates/precision/addon_registry.yaml`](../templates/precision/addon_registry.yaml)
- [`templates/precision/validation_report.example.json`](../templates/precision/validation_report.example.json)
- [`templates/precision/codex_config.toml`](../templates/precision/codex_config.toml)
- [`templates/precision/.mcp.json`](../templates/precision/.mcp.json)
- [`templates/precision/plugin.json`](../templates/precision/plugin.json)
- [`templates/precision/agents/AGENTS.md`](../templates/precision/agents/AGENTS.md)
- [`templates/precision/skills/precise-blender-modeling/SKILL.md`](../templates/precision/skills/precise-blender-modeling/SKILL.md)
- [`templates/precision/subagents/scene-validator.toml`](../templates/precision/subagents/scene-validator.toml)
- [`templates/precision/subagents/visual-reviewer.toml`](../templates/precision/subagents/visual-reviewer.toml)
- [`templates/precision/subagents/addon-auditor.toml`](../templates/precision/subagents/addon-auditor.toml)

schema:

- [`schemas/precision/model_spec.schema.json`](../schemas/precision/model_spec.schema.json)
- [`schemas/precision/validation_report.schema.json`](../schemas/precision/validation_report.schema.json)
- [`schemas/precision/addon_registry.schema.json`](../schemas/precision/addon_registry.schema.json)

## 使い分け

`templates/precision/` は利用者環境や installer へコピーする配布物です。`schemas/precision/` は template と実行結果の検証契約です。

`codex_config.toml` の `command` / `args` は MCP server 起動設定であり、tool の実行時引数ではありません。公開 tool は sidecar server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で制御します。

`agents/AGENTS.md` は利用者のプロジェクトへ配置する作業指示 template です。`skills/precise-blender-modeling/SKILL.md` は Codex skill directory へコピーして利用します。`subagents/*.toml` は検証、視覚レビュー、add-on 監査の役割分担に使います。

## template / schema validation

template と schema の整合性は次のコマンドで確認します。

```powershell
uv run --with pyyaml --with jsonschema python scripts\validate_precision_templates.py
```

確認内容:

- `model_spec.yaml` が `model_spec.schema.json` に一致する
- `addon_registry.yaml` が `addon_registry.schema.json` に一致する
- `validation_report.example.json` が `validation_report.schema.json` に一致する
- `codex_config.toml` に `mcp_servers.blender_precision` と基本 timeout / disabled tool が含まれる

## installer からの任意導入

headless で precision profile を含める場合:

```powershell
uv run blender-mcp-installer --headless --include-precision-profile
```

実行予定 step だけ確認する場合:

```powershell
uv run blender-mcp-installer --plan --include-precision-profile
```

GUI では `Also install v2 precision profile templates, Skill, and subagent files.` を有効にすると、precision profile 配布物を Codex home 配下へコピーします。

## scene generation

`create_or_update_scene_from_spec` は、`model_spec.yaml` の `objects` / `materials` / `validation` を読み込み、Blender scene を生成または更新する tool です。

初期対応 shape:

- `box`
- `sphere`
- `cylinder`
- `cone`
- `torus`

反映する主な項目:

- `objects[].name`
- `objects[].type`
- `objects[].collection`
- `objects[].dimensions`
- `objects[].location`
- `objects[].rotation`
- `objects[].material`
- `objects[].requirements.bevel_radius`
- `materials[].color`
- `materials[].roughness`
- `materials[].metallic`

`validation.require_camera=true` の場合は `Precision_Camera` を標準配置し、`validation.require_lights=true` の場合は `Precision_Key_Light` を標準配置します。

dry-run で生成予定だけ確認する場合:

```powershell
uv run python -c "from blender_precision_mcp.scene_builder import create_or_update_scene_from_spec; import json; print(json.dumps(create_or_update_scene_from_spec('templates/precision/model_spec.yaml', dry_run=True), ensure_ascii=False, indent=2))"
```

Blender Python が使えない環境で `dry_run=false` を指定した場合は、`error.code=blender_unavailable` を返します。

## live scene validation

`validate_scene_against_spec` は、通常の schema / static check に加えて `live_scene=true` で Blender live scene の実測値を report に含められます。

確認する主な値:

- `objects[].name` が Blender scene に存在すること
- `objects[].dimensions` が `validation.max_dimension_error_m` の範囲内で一致すること
- `objects[].location` が `validation.max_location_error_m` の範囲内で一致すること
- `objects[].material` が live scene の material slot に割り当てられていること
- `validation.require_camera` が true の場合、active camera が存在すること
- `validation.require_lights` が true の場合、light object が存在すること

Blender Python が使えない環境では、report は `live_scene.available=false` と `error.code=BLENDER_NOT_AVAILABLE` を返します。

公式 Blender MCP で scene snapshot を取得できる場合は、`live_scene_snapshot` として `validate_scene_against_spec` に渡せます。この場合、validation は sidecar 側の Python 依存で実行し、Blender 側は scene inspection だけを担当します。

## visual QA

`capture_review_views` は `visual_qa.views` に定義された front / side / top / perspective の review image を保存し、`review_manifest.json` に撮影条件と品質チェック結果を残します。

manifest に含める主な値:

- `views`: 撮影した view 名
- `resolution`: 出力画像サイズ
- `target_objects`: `model_spec.yaml` に定義された確認対象 object
- `captures[]`: view、画像パス、camera、対象 object
- `quality_checks[]`: blank check と bounding box check の結果
- `errors[]`: Blender 未起動、対象 object 不在、未対応 view などの structured error

dry-run で manifest 形式だけ確認する場合:

```powershell
uv run python scripts\capture_precision_review_views.py --dry-run --views front,top --output-dir outputs\reviews\dry-run
```

実 screenshot を保存するには Blender Python から実行します。Blender bundled Python に PyYAML がない環境でも最低限 `objects` と `visual_qa` を読める fallback parser を使います。

品質チェック:

- `blank_check`: 画像が背景色だけに近い場合に failed
- `bounding_box_check`: 背景と異なる pixel の bounding box が小さすぎる場合に failed

現在の自動チェックは最低限の破綻検知です。キャラクターらしさ、意図した表情、構図の良し悪しは `captures[]` の画像を人が確認します。

## mesh quality / cleanup

`analyze_mesh_quality` は Blender scene の mesh object を検査し、`model_spec.yaml` の `mesh_quality.defaults` と `mesh_quality.objects[]` の threshold に照合します。

取得する主な値:

- `vertex_count`
- `edge_count`
- `face_count`
- `triangle_count`
- `quad_count`
- `ngon_count`
- `triangle_ratio`
- `quad_ratio`
- `loose_vertices`
- `loose_edges`
- `non_manifold_edges`

対応する主な threshold:

- `max_non_manifold_edges`
- `max_loose_vertices`
- `max_loose_edges`
- `max_face_count`
- `min_quad_ratio`

Blender Python が使えない環境では `error.code=blender_unavailable` を返します。

cleanup は `apply_mesh_cleanup` から実行します。安全のため、通常はまず `dry_run=true` で予定操作を確認し、実行時は `confirm=true` と `create_backup=true` を必須にします。

dry-run 例:

```powershell
uv run python -c "from blender_precision_mcp.mesh_quality import apply_mesh_cleanup; import json; print(json.dumps(apply_mesh_cleanup('example_body', dry_run=True), ensure_ascii=False, indent=2))"
```

live smoke 手順:

1. Blender を起動し、公式 MCP add-on を接続する
2. `create_or_update_scene_from_spec` で `model_spec.yaml` から scene を生成する
3. `analyze_mesh_quality(target_objects=['example_body'])` を Blender 内 Python または公式 Blender MCP 経由で実行する
4. cleanup が必要な場合は `apply_mesh_cleanup(target_object='example_body', dry_run=True)` を確認する
5. 予定操作に問題がなければ `apply_mesh_cleanup(target_object='example_body', dry_run=False, confirm=True, create_backup=True)` を実行する
6. `validate_retopology_result(target_object='example_body')` で threshold を再確認する

## approved add-on operator

`addon_registry.yaml` に登録した operator は、`run_approved_addon_operator` または `apply_retopology` から実行します。

安全導線:

1. `dry_run=true` で preview し、operator、parameter、context、`safety_actions` を確認する
2. destructive operator は `confirm=true` がない限り実行しない
3. `backup_required=true` の operator は、実行前に target object または active object を duplicate する
4. 実行結果には backup object 名、operator result、structured error を残す

主な error code:

- `not_approved`: registry に登録されていない operator
- `confirmation_required`: destructive operator に `confirm=true` がない
- `backup_policy_violation`: destructive operator が backup 必須になっていない
- `backup_failed`: backup 作成に失敗
- `context_not_ready`: active object / selected object / mode などの context が不足
- `operator_missing`: Blender に operator が登録されていない
- `operator_execution_failed`: operator 実行時例外

実行例:

```powershell
uv run python scripts\inspect_precision_addons.py --mode operators
```

実 operator の live 実行は Blender 内 Python または公式 Blender MCP から行います。まず `dry_run=true`、次に `confirm=true` の順で実行し、backup が作成されたことを確認します。
