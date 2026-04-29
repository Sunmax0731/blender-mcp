# 旧独自構成の在庫

このドキュメントは、公式 Blender MCP へ移行する過程で残っている旧独自構成を整理するための在庫表です。

## 1. 現在の扱い

- `blender_addon/blender_mcp/` は旧独自 add-on 実装
- `src/blender_mcp_server/` は旧独自 MCP server 実装
- `scripts/legacy/` 配下は旧独自構成を前提にした自動化

これらは当面、比較・移行・参考のために保持するが、主経路としては扱わない。

## 2. 分類

### 2.1 隔離候補

- `blender_addon/blender_mcp/`
- `src/blender_mcp_server/`
- `tests/test_command_*`
- `tests/test_ai_service.py`
- `tests/test_http_client.py`
- `tests/test_session_operator.py`

### 2.2 転用候補

- `scripts/blender_ui_capture.py`
- `scripts/prepare_blender_window.py`
- `scripts/reload_running_blender.py`

### 2.3 継続利用候補

- `scripts/install_official_blender_mcp.ps1`
- `scripts/install_official_blender_mcp.cmd`

## 3. 次の整理方針

1. 旧独自構成を `legacy/` などへ隔離するか判断する
2. 公式構成でも使える自動化だけ抽出する
3. 旧独自構成前提のテストと docs を段階的に削除する
4. 公式構成でのテスト項目へ置き換える

## 4. 現在の隔離先

- `scripts/legacy/blender_automation.py`
- `scripts/legacy/build_blender_addon.py`
- `scripts/legacy/sync_blender_addon.py`
- `scripts/legacy/update_blender_addon.ps1`
- `scripts/legacy/update_blender_addon.cmd`
- `scripts/legacy/run_blender_ui_smoke.ps1`
- `scripts/legacy/run_blender_prompt_smoke.ps1`
