# v1.0.0 release manifest

## 1. Generated asset

| Asset | Path | Size | SHA-256 |
| --- | --- | ---: | --- |
| `blender-mcp-installer.exe` | `dist/one-click-installer/blender-mcp-installer.exe` | `10278473` bytes | `dbfa0023377980110c4ae5011ca43a904b126eec4e01745f99f56f0955b44a41` |
| `blender-mcp-installer.exe.sha256` | `dist/one-click-installer/blender-mcp-installer.exe.sha256` | `93` bytes | Generated from the exe |
| `release-manifest-v1.0.0.json` | `dist/one-click-installer/release-manifest-v1.0.0.json` | `1298` bytes | Manifest file |

Generated at: `2026-04-30`

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
uv run blender-mcp-installer --plan
```

```powershell
uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender
```

## 4. Release upload targets

Upload these files to GitHub Release `v1.0.0`:

- `dist/one-click-installer/blender-mcp-installer.exe`
- `dist/one-click-installer/blender-mcp-installer.exe.sha256`
- `dist/one-click-installer/release-manifest-v1.0.0.json`

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

The installer exe is the only executable asset for v1.0.0. v2 precision profile is included as optional experimental support.
