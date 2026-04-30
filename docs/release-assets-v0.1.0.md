# v0.1.0 release assets

## 1. 添付するもの

GitHub Release `v0.1.0` には次を添付する。

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v0.1.0.json`

## 2. 添付しないもの

次は GitHub Release asset として添付しない。

- 公式 Blender MCP zip
- Blender 本体
- Codex App 本体
- Python 仮想環境
- `.venv/`
- `.official-mcp-venv/`
- `artifacts/` 配下の検証ログ一式
- `tmp/` 配下の作業ファイル
- PyInstaller build cache

## 3. 理由

公式 Blender MCP zip は公式配布物であり、このリポジトリの Release asset として再配布しない。installer は導入時に公式配布元または取得済みキャッシュを使う。

仮想環境、検証 artifact、build cache は利用者が直接使う配布物ではなく、環境差や不要なサイズ増加の原因になるため添付しない。

## 4. 生成元

`blender-mcp-installer.exe` は次で生成する。

```powershell
uv sync --python 3.11 --extra dev
.\scripts\build_installer_exe.ps1
```

生成先:

```text
dist/one-click-installer/blender-mcp-installer.exe
```

## 5. M2 で作成する証跡

M2: Packaging and installer validation では、次を作成して Issue に記録する。

- file size
- SHA-256 checksum
- build command
- build log path
- validation commands
- upload 対象 asset 一覧

## 6. Release 前チェック

- Release asset に添付しないものが混入していない
- checksum が実ファイルと一致している
- manifest の asset 名、file size、checksum が一致している
- release notes の添付 asset 記載と一致している
