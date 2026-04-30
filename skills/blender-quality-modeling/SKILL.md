---
name: blender-quality-modeling
description: Create higher quality Blender models through Blender MCP or Blender Python workflows. Use when Codex is asked to make, improve, review, or validate a Blender scene or 3D model and should include object structure, materials, lighting, camera setup, naming, render evidence, and quality checks.
---

# Blender Quality Modeling

## Workflow

1. Clarify the target scene, subject, style, and required deliverables when they are missing.
2. Plan the model as named parts before generating geometry.
3. Use non-destructive or easy-to-edit primitives first, then add detail where it improves recognition.
4. Assign materials intentionally: base color, roughness, metallic/specular behavior, and named material slots.
5. Add lighting and a camera suitable for validation, not only object creation.
6. Render or capture evidence and inspect it for framing, missing parts, material assignment, and scale problems.
7. Report the created collection/object names, materials, render path, and remaining limitations.

## Modeling Standards

- Create a dedicated collection for generated work.
- Use descriptive object and material names.
- Keep the default scene clean unless the user asks to preserve existing objects.
- Prefer multiple simple named meshes over one opaque mesh when the subject has recognizable parts.
- Add bevels, smoothing, or subdivision only where they improve the result and remain performant.
- Include camera, lights, and world/background settings when the user expects a visual result.
- Save a `.blend` or render artifact when the task asks for a reusable or reviewable output.

## Safety

- Do not delete unrelated scene content without explicit instruction.
- For destructive edits, create a backup collection or require confirmation.
- Avoid unrestricted arbitrary `bpy` execution in user-facing workflows.
- Keep generated assets local unless the user explicitly asks to publish or upload them.

## Quality Checklist

Before finishing, verify:

- The model is visible from the active camera.
- Main subject parts are present and named.
- Materials are assigned to every visible generated mesh.
- Lighting is sufficient to inspect shape and color.
- Render or screenshot evidence is not blank, overly cropped, or from the wrong angle.
- The final response includes the output path and any known limitations.

## Reference

For detailed criteria, read `references/model-quality-checklist.md` when the task involves a polished model, reusable scene, user-facing example, or quality review.
