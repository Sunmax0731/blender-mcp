# v1.2.0 release manifest

## 1. Release assets

| Asset | Path | Notes |
| --- | --- | --- |
| `blender-mcp-installer.exe` | `dist/one-click-installer/blender-mcp-installer.exe` | Windows one-click installer |
| `blender-mcp-installer.exe.sha256` | `dist/one-click-installer/blender-mcp-installer.exe.sha256` | SHA256 checksum |
| `release-manifest-v1.2.0.json` | `dist/one-click-installer/release-manifest-v1.2.0.json` | Asset manifest |

## 2. Build command

```powershell
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
uv run blender-mcp-installer --plan --skip-third-party-plugins --no-launch-blender
```

```powershell
uv run python -m compileall src blender_addon
```

## 4. GitHub Release へ添付するもの

- `dist/one-click-installer/blender-mcp-installer.exe`
- `dist/one-click-installer/blender-mcp-installer.exe.sha256`
- `dist/one-click-installer/release-manifest-v1.2.0.json`
