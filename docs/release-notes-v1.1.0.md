# blender-mcp v1.1.0

`v1.1.0` は、公式 Blender MCP 導入に加えて、任意機能の precision workflow を強化する Release です。

通常の利用者はこれまでどおり `blender-official` MCP server から Blender を操作できます。precision profile を有効にした場合は、`model_spec`、validation、visual QA、mesh quality、export manifest を扱う `blender_precision` MCP server も利用できます。

## 主な変更

- `model_spec` から Blender scene を生成・更新する `create_or_update_scene_from_spec` を追加
- `create_parametric_object` と `assign_materials_from_spec` を追加
- mesh 品質を確認する `analyze_mesh_quality` を追加
- backup / confirm 前提の `apply_mesh_cleanup` を追加
- `.blend` / `.glb` 出力と `export_manifest.json` を作成する `export_scene` を追加
- precision workflow smoke script を追加
- precision profile 導入時に installer-managed venv から `blender_precision` MCP server を起動できるように変更
- 公式 Blender MCP Example 1: Scene Analysis / Example 2: Various Prompts の利用者向け手順を整理

## 利用者向け prompt 例

### 1. 丸いキャラクターモデルを作る

```text
Blenderでカービィ風の丸いキャラクターモデルを作成してください。
体はピンクの球体、手は左右に小さな丸い腕、足は赤い楕円形にしてください。
大きな青い目、白いハイライト、黒い瞳、赤い口、左右のピンクの頬も作成してください。

各パーツには分かりやすい名前を付け、マテリアルで色を設定してください。
ライトとカメラも配置し、正面から見やすい構図にしてください。
最後にシーン全体を確認し、作成したオブジェクト一覧と工夫した点を説明してください。
```

### 2. Scene Analysis

```text
現在開いている Blender scene を解析し、object 構成、material、light、camera、品質上の懸念、改善案を日本語でまとめてください。
特に camera から見た表示サイズに対して polygon 数が多すぎる object があれば、理由と最適化案を説明してください。
```

### 3. material 利用状況を確認する

```text
現在の scene で、指定した material を使っている object を一覧化してください。
object 名、collection、material slot、見た目の用途を表にしてください。
```

### 4. precision workflow の証跡を残す

```text
model_spec に基づいて scene を生成し、validation report、visual QA manifest、export manifest を同じ artifact directory に保存してください。
最後に生成した artifact の一覧と、確認すべき残課題を説明してください。
```

### 5. mesh 品質を確認する

```text
現在の scene の mesh 品質を確認してください。
loose vertices、loose edges、non-manifold edges、face count、triangle / quad ratio を確認し、問題がある object と改善案を説明してください。
cleanup を実行する場合は、必ず dry-run の結果を先に提示してください。
```

## precision profile について

precision profile は optional experimental 機能です。通常の公式 Blender MCP 導入だけを使う場合は有効にしなくても構いません。

有効にすると、installer は次を追加します。

- Codex home 配下の precision template
- `precise-blender-modeling` Skill
- subagent template
- installer-managed venv
- Codex App の `[mcp_servers.blender_precision]` 設定

`blender_precision` は公開 `uvx` package ではなく、installer が作成したローカル venv から起動します。

## 検証

Release 前に次を確認します。

- `uv run pytest`
- `uv run --with pyyaml --with jsonschema python scripts\validate_precision_templates.py`
- `uv run python scripts\run_precision_workflow_smoke.py --output-dir artifacts\precision-workflow-smoke`
- packaged installer の `--plan`
- packaged installer の headless smoke

## GitHub Release に添付するもの

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v1.1.0.json`

