# AGENTS.md - Blender precision modeling project rules

## General modeling rules

- Use metric units unless the user explicitly specifies otherwise.
- Treat 1 Blender unit as 1 meter by default.
- Before editing Blender, create or update `model_spec.yaml`.
- Prefer deterministic, parameterized operations over vague visual placement.
- Name all objects, materials, collections, cameras, and lights semantically.
- Keep the main object centered at the world origin unless the spec says otherwise.
- Apply scale transforms before final validation.

## MCP tool usage

- Prefer high-level MCP tools such as `create_or_update_scene_from_spec`, `validate_scene_against_spec`, `analyze_mesh_quality`, and `capture_review_views`.
- Do not use arbitrary `execute_blender_code` in normal workflows.
- If a task cannot be done through approved high-level tools, explain the limitation and propose a wrapper tool instead of directly running free-form code.

## Add-on usage

- Use Blender add-ons only when they are installed, enabled, approved in the addon registry, and automatable from Python.
- Prefer wrapper tools such as `apply_retopology`, `apply_mesh_cleanup`, `apply_uv_unwrap`, and `transfer_mesh_data` over direct operator calls.
- Do not run unknown add-ons or unapproved operators.
- Do not use UI-only, modal, brush, or mouse-interaction operators unless the tool explicitly supports them.
- Record addon module, display name, version, operator/API used, and parameters.

## Destructive operations

- Always create a backup before destructive mesh edits, retopology, remesh, decimate, UV overwrite, modifier apply, or object deletion.
- Never delete existing user objects unless the task explicitly asks for deletion or replacement.
- If an operation fails, keep the backup and report the failure reason.

## Validation

- After Blender changes, run scene validation.
- After mesh editing or retopology, run mesh quality validation.
- Capture front, side, top, and perspective review images before final response.
- Report validation failures, warnings, assumptions, and remaining limitations.

## Output

- Save validation reports under `outputs/reports/`.
- Save preview images under `outputs/previews/`.
- Save exported assets under `outputs/exports/`.
- Include operation logs for add-on-assisted workflows.
