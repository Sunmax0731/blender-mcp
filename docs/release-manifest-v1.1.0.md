# v1.1.0 release manifest

## 1. Release assets

| Asset | Path | Size | Notes |
| --- | --- | ---: | --- |
| `blender-mcp-installer.exe` | `dist/one-click-installer/blender-mcp-installer.exe` | generated | Windows one-click installer |
| `blender-mcp-installer.exe.sha256` | `dist/one-click-installer/blender-mcp-installer.exe.sha256` | generated | Generated from the exe |
| `release-manifest-v1.1.0.json` | `dist/one-click-installer/release-manifest-v1.1.0.json` | generated | Manifest file |

## 2. Build command

```powershell
.\scripts\build_installer_exe.ps1
```

## 3. Validation commands

```powershell
uv run pytest
```

```powershell
uv run --with pyyaml --with jsonschema python scripts\validate_precision_templates.py
```

```powershell
uv run python scripts\run_precision_workflow_smoke.py --output-dir artifacts\precision-workflow-smoke
```

```powershell
.\dist\one-click-installer\blender-mcp-installer.exe --plan --include-precision-profile --no-launch-blender
```

## 4. Release upload targets

Upload these files to GitHub Release `v1.1.0`:

- `dist/one-click-installer/blender-mcp-installer.exe`
- `dist/one-click-installer/blender-mcp-installer.exe.sha256`
- `dist/one-click-installer/release-manifest-v1.1.0.json`

