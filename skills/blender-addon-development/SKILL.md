---
name: blender-addon-development
description: Build, review, or improve Blender add-ons. Use when Codex is asked to design or implement Blender extensions/add-ons, panels, operators, properties, registration, manifests, packaging, or validation workflows for Blender Python add-on development.
---

# Blender Add-on Development

## Workflow

1. Identify the target Blender version, add-on type, user workflow, and distribution format.
2. Define the add-on boundary: operators, panels, properties, preferences, and data touched.
3. Keep registration explicit and reversible with `register()` and `unregister()`.
4. Prefer small operators and panels over one large script.
5. Avoid changing global Blender state unless the user action clearly requires it.
6. Validate import, registration, UI availability, and operator behavior.
7. Document manual smoke steps when Blender UI validation is required.

## Implementation Standards

- Use `bl_info` for legacy add-ons or `blender_manifest.toml` for extension-style packaging, matching the target distribution.
- Put UI in predictable Blender areas, usually `VIEW_3D` Sidebar for scene tools.
- Use `bpy.props` for user-editable settings and keep defaults safe.
- Use `poll()` on operators when context matters.
- Keep file writes, deletion, and scene-wide edits behind explicit user actions.
- Store user-facing labels and descriptions clearly; avoid exposing internal migration terms.

## Validation

Before finishing, verify as much as the environment allows:

- Python files import without syntax errors.
- `register()` and `unregister()` can run without leaving duplicate classes or properties.
- Operators have stable `bl_idname` values.
- Panels appear in the intended UI region.
- Destructive operators require confirmation or use Blender's undo flow.
- README or docs include install, enable, and smoke-test steps when the add-on is user-facing.

## References

Read `references/addon-patterns.md` when implementing or reviewing actual add-on code, packaging, or validation steps.
