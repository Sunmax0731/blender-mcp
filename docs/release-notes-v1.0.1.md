# blender-mcp v1.0.1

`v1.0.1` は、`v1.0.0` installer の precision profile 任意導入で発生した不具合を修正する hotfix Release です。

## 修正内容

- packaged installer 起動時に、`scripts` だけでなく `templates` も `%LOCALAPPDATA%\BlenderMcpInstaller` へ展開するように修正しました。
- これにより、precision profile 導入 step が `templates\precision` を見つけられず失敗する問題を修正しました。

## 対象のエラー

```text
[STEP 5/6] precision-profile
[DESC] Install optional precision profile templates, Skill, and subagent files.
[CMD] powershell -NoProfile -ExecutionPolicy Bypass -File ...\install_precision_profile.ps1 -MergeCodexConfig
[EXIT] 1
[FAILED] precision-profile
```

直接実行時の原因:

```text
Precision template root not found: ...\BlenderMcpInstaller\templates\precision
```

## 検証

- `uv run pytest`: 58 passed
- packaged exe `--plan --include-precision-profile --no-launch-blender`: OK
- packaged runtime root に `templates\precision\codex_config.toml` が展開されることを確認
- 展開後の `install_precision_profile.ps1 -PlanConfigMerge`: exit 0

## GitHub Release に添付するもの

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v1.0.1.json`

## 既知制約

`v1.0.0` と同じく、v2 precision profile は optional experimental です。通常の公式 Blender MCP 導入だけを使う場合は、precision profile を有効にする必要はありません。
