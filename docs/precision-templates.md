# v2 precision template / schema

v2 precision modeling で使う配布用 template と schema を管理するドキュメントです。

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

`templates/precision/` は利用者環境や installer へコピーする配布物です。
`schemas/precision/` は template と実行結果の検証契約です。

`codex_config.toml` の `command` / `args` は MCP server 起動設定であり、tool の実行時引数ではありません。公開 tool は sidecar server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で制御します。

`agents/AGENTS.md` は利用者プロジェクトへ置く作業指示 template です。`skills/precise-blender-modeling/SKILL.md` は Codex skill directory へコピーして使います。`subagents/*.toml` は検証、視覚レビュー、add-on 監査の役割分担に使います。

## template / schema validation

template と schema の整合性は次で確認します。

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

## live scene validation

`validate_scene_against_spec` は、通常の schema / static check に加えて `live_scene=true` で Blender live scene の実測値を report に含められます。

確認する主な値:

- `objects[].name` が Blender scene に存在すること
- `objects[].dimensions` が `validation.max_dimension_error_m` の範囲内で一致すること
- `objects[].location` が `validation.max_location_error_m` の範囲内で一致すること
- `objects[].material` が live scene の material slot に割り当てられていること
- `validation.require_camera` が true の場合、active camera が存在すること
- `validation.require_lights` が true の場合、light object が存在すること

Blender Python が使えない環境では、report は `live_scene.available=false` と `error.code=BLENDER_NOT_AVAILABLE` を返します。これにより、Blender 未起動または Blender 外実行の失敗を structured error として扱えます。

公式 Blender MCP で scene snapshot を取得できる場合は、`live_scene_snapshot` として `validate_scene_against_spec` に渡せます。この場合、validation は sidecar 側の Python 依存で実行し、Blender 側は scene inspection だけを担当します。

Python からの実行例:

```powershell
uv run python -c "from blender_precision_mcp.validation import validate_model_spec; import json; print(json.dumps(validate_model_spec('templates/precision/model_spec.yaml', live_scene=True), ensure_ascii=False, indent=2))"
```

上記を通常 Python で実行した場合は `BLENDER_NOT_AVAILABLE` になります。Blender 内 Python または公式 Blender MCP から取得した snapshot を渡した場合は、現在の scene から object / material / camera / light の実測値を検証できます。

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
