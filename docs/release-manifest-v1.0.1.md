# v1.0.1 release manifest

## 1. Generated asset

| Asset | Path | Size | SHA-256 |
| --- | --- | ---: | --- |
| `blender-mcp-installer.exe` | `dist/one-click-installer/blender-mcp-installer.exe` | `10279876` bytes | `2677dad51f9d24e0036d84b4b3459056ceb9de971a23ea62359cbf81c005ffc7` |
| `blender-mcp-installer.exe.sha256` | `dist/one-click-installer/blender-mcp-installer.exe.sha256` | `93` bytes | Generated from the exe |
| `release-manifest-v1.0.1.json` | `dist/one-click-installer/release-manifest-v1.0.1.json` | generated | Manifest file |

## 2. Fix

`v1.0.1` fixes packaged runtime extraction for precision profile templates.

## 3. Validation commands

```powershell
uv run pytest
```

```powershell
.\dist\one-click-installer\blender-mcp-installer.exe --plan --include-precision-profile --no-launch-blender
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\BlenderMcpInstaller\scripts\install_precision_profile.ps1" -PlanConfigMerge
```

## 4. Release upload targets

Upload these files to GitHub Release `v1.0.1`:

- `dist/one-click-installer/blender-mcp-installer.exe`
- `dist/one-click-installer/blender-mcp-installer.exe.sha256`
- `dist/one-click-installer/release-manifest-v1.0.1.json`
