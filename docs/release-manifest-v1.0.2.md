# v1.0.2 release manifest

## 1. Generated asset

| Asset | Path | Size | SHA-256 |
| --- | --- | ---: | --- |
| `blender-mcp-installer.exe` | `dist/one-click-installer/blender-mcp-installer.exe` | `10276555` bytes | `4b79a3e3ebe4ea12988c22a6cd14e9675b83f3021da93a0eff241ef3544ba8bf` |
| `blender-mcp-installer.exe.sha256` | `dist/one-click-installer/blender-mcp-installer.exe.sha256` | `93` bytes | Generated from the exe |
| `release-manifest-v1.0.2.json` | `dist/one-click-installer/release-manifest-v1.0.2.json` | generated | Manifest file |

## 2. Fix

`v1.0.2` stops auto-registering the experimental `blender_precision` MCP server and cleans up the generated section from previous installs.

## 3. Validation commands

```powershell
uv run pytest
```

```powershell
.\dist\one-click-installer\blender-mcp-installer.exe --plan --include-precision-profile --no-launch-blender
```
