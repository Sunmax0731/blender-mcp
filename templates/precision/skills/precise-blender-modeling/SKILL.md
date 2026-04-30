---
name: precise-blender-modeling
description: Use for precise Blender modeling tasks involving BlenderMCP, model specs, validation, visual QA, mesh cleanup, retopology, or approved Blender add-ons.
---

# Precise Blender Modeling Workflow

## Goal

Create, modify, validate, and export Blender scenes through a specification-driven workflow. Use approved Blender add-ons only through safe wrapper tools.

## Workflow

1. Parse the user request into `model_spec.yaml`.
2. Identify missing dimensions, materials, topology needs, and export requirements.
3. Make reasonable assumptions only when necessary and record them in the spec.
4. Build or update the scene using high-level MCP tools.
5. Run `validate_scene_against_spec`.
6. If mesh cleanup or retopology is needed:
   - Run `analyze_mesh_quality` first.
   - Check approved add-ons and available methods.
   - Create a backup before destructive operations.
   - Use `apply_mesh_cleanup` or `apply_retopology` rather than raw add-on calls.
   - Run `validate_retopology_result` after the operation.
7. Capture review views from front, side, top, and perspective.
8. Review visual issues: missing parts, scale mismatch, floating objects, material errors, broken topology, poor silhouette.
9. Repair validation or visual issues.
10. Export only after validation passes or remaining warnings are explicitly reported.

## Preferred tools

- `get_scene_snapshot`
- `create_or_update_scene_from_spec`
- `validate_scene_against_spec`
- `analyze_mesh_quality`
- `capture_review_views`
- `list_blender_addons`
- `inspect_addon_capabilities`
- `apply_retopology`
- `apply_mesh_cleanup`
- `export_scene`

## Avoid

- Free-form `execute_blender_code` in normal workflows.
- Unknown add-ons.
- Unapproved add-on operators.
- UI-only or modal operators.
- Destructive mesh editing without backup.
- Final responses without validation results.

## Final report format

Report:

- Spec path used.
- Tools used.
- Add-ons used, if any.
- Validation status.
- Mesh quality status, if relevant.
- Preview artifacts.
- Exports.
- Remaining assumptions or warnings.
