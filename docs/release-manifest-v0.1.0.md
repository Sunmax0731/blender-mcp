# v0.1.0 release manifest

## 1. Generated asset

| Asset | Path | Size | SHA-256 |
| --- | --- | ---: | --- |
| `blender-mcp-installer.exe` | `dist/one-click-installer/blender-mcp-installer.exe` | `10278993` bytes | `6adf359ced179f3d4a58cbf996e1e4046d609be97f4be7c8bb81ef3486d9242e` |
| `blender-mcp-installer.exe.sha256` | `dist/one-click-installer/blender-mcp-installer.exe.sha256` | `93` bytes | Generated from the exe |
| `release-manifest-v0.1.0.json` | `dist/one-click-installer/release-manifest-v0.1.0.json` | `1460` bytes | Manifest file |

Generated at: `2026-04-30T05:20:29Z`

## 2. Build command

```powershell
uv sync --python 3.11 --extra dev
.\scripts\build_installer_exe.ps1
```

## 3. Validation commands

```powershell
uv run pytest
```

```powershell
uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender
```

```powershell
uv run --with pyyaml --with jsonschema python scripts\validate_precision_templates.py
```

## 4. Release upload targets

Upload these files to GitHub Release `v0.1.0`:

- `dist/one-click-installer/blender-mcp-installer.exe`
- `dist/one-click-installer/blender-mcp-installer.exe.sha256`
- `dist/one-click-installer/release-manifest-v0.1.0.json`

## 5. Excluded assets

Do not upload:

- official Blender MCP zip
- Blender installer
- Codex App installer
- `.venv/`
- `.official-mcp-venv/`
- `artifacts/`
- `tmp/`
- PyInstaller build cache

## 6. Notes

The installer exe is the only executable asset for v0.1.0. v2 precision profile files are bundled into the installer support data and can also be read from the source tree.
