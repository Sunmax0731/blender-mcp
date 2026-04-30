# Model Quality Checklist

Use this reference when a Blender MCP task needs a polished or user-facing result.

## Shape

- Break the subject into recognizable components.
- Use correct relative scale between body parts, props, and environment.
- Add simple secondary forms that help recognition: eyes, seams, handles, feet, buttons, trims, highlights.
- Avoid leaving default cube/camera/light clutter unless it is part of the scene.

## Materials

- Name materials by purpose, not only color.
- Use roughness/specular values to distinguish plastic, metal, glass, skin, fabric, and matte surfaces.
- Add small highlights or accent materials when the reference depends on them.
- Check that all generated visible meshes have a material slot.

## Scene Presentation

- Put generated objects in a dedicated collection.
- Add at least one key light and one camera for reviewable output.
- Frame the model so the whole subject is visible unless the requested deliverable is a close-up.
- Use render resolution and samples appropriate for quick validation.

## Validation Evidence

- Render or capture a screenshot after generation.
- Inspect the result for missing parts, wrong orientation, unassigned materials, and accidental cropping.
- If the model is meant for documentation, save a PNG under a docs-friendly or artifacts path and include it in the report.

## Final Report

Include:

- Collection name
- Important object names
- Material names or material groups
- Render/screenshot path
- `.blend` path when saved
- Known limitations or follow-up improvements
