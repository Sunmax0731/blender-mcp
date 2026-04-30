# v1.0.3 release manifest

## 1. Generated asset

| Asset | Path | Size | SHA-256 |
| --- | --- | ---: | --- |
| `blender-mcp-installer.exe` | `dist/one-click-installer/blender-mcp-installer.exe` | `10280752` bytes | `8c13309d339874ba0cb2c4008d88bdbb8f4cd77716b62708358e442752a3af4b` |
| `blender-mcp-installer.exe.sha256` | `dist/one-click-installer/blender-mcp-installer.exe.sha256` | `93` bytes | Generated from the exe |
| `release-manifest-v1.0.3.json` | `dist/one-click-installer/release-manifest-v1.0.3.json` | generated | Manifest file |

## 2. Fix

`v1.0.3` adds a cleanup step that removes obsolete `blender_mcp` registration from previous development builds while keeping the official Blender MCP add-on enabled.

## 3. Validation commands

```powershell
uv run pytest
```

```powershell
uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender
```

```powershell
.\dist\one-click-installer\blender-mcp-installer.exe --plan --include-precision-profile --no-launch-blender
```

```powershell
.\dist\one-click-installer\blender-mcp-installer.exe --headless --include-precision-profile --no-launch-blender
```

```powershell
.\scripts\remove_blender_prompt_ui.ps1
```
