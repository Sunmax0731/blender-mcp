# Blender Add-on Patterns

## File Structure

For small add-ons:

```text
addon_name/
  __init__.py
```

For larger add-ons:

```text
addon_name/
  __init__.py
  operators/
  panels/
  properties.py
  preferences.py
```

For Blender extension packaging, include `blender_manifest.toml` at the package root when targeting the extension workflow.

## Registration

- Keep a single ordered `classes` tuple.
- Register properties after classes when they depend on registered types.
- Unregister in reverse order.
- Remove custom properties from Blender types in `unregister()`.

## Operator Design

- Use `bl_idname` with a stable namespace such as `object.my_tool_action`.
- Use `poll()` when the operator requires an active object, selected objects, or a specific mode.
- Return `{'FINISHED'}` only after the operation actually succeeds.
- Return `{'CANCELLED'}` and report a clear error when preconditions fail.

## Panel Design

- Choose `bl_space_type`, `bl_region_type`, and `bl_category` intentionally.
- Keep panels compact; put advanced actions behind separate operators or collapsible UI.
- Labels should describe the user action, not the internal implementation.

## Validation Commands

Possible validation approaches:

- Python syntax check with the project test runner.
- Blender background import and register smoke.
- Manual UI smoke in Blender when panels or operators need visible confirmation.

Record the exact command, Blender version, and observed result in the Issue comment.
