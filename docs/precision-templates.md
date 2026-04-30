# v2 precision template / schema

v2 precision modeling で使う配布用 template と schema は、正式配置先を分けて管理する。

## 配置

template:

- [`templates/precision/blender_precision_config.yaml`](../templates/precision/blender_precision_config.yaml)
- [`templates/precision/model_spec.yaml`](../templates/precision/model_spec.yaml)
- [`templates/precision/addon_registry.yaml`](../templates/precision/addon_registry.yaml)
- [`templates/precision/validation_report.example.json`](../templates/precision/validation_report.example.json)
- [`templates/precision/codex_config.toml`](../templates/precision/codex_config.toml)
- [`templates/precision/.mcp.json`](../templates/precision/.mcp.json)
- [`templates/precision/plugin.json`](../templates/precision/plugin.json)

schema:

- [`schemas/precision/model_spec.schema.json`](../schemas/precision/model_spec.schema.json)
- [`schemas/precision/validation_report.schema.json`](../schemas/precision/validation_report.schema.json)
- [`schemas/precision/addon_registry.schema.json`](../schemas/precision/addon_registry.schema.json)

## 使い分け

`templates/precision/` は、利用者環境や installer へコピーする配布元として扱う。`schemas/precision/` は、template と実行結果の検証契約として扱う。

`codex_config.toml` の `command` / `args` は MCP server 起動設定であり、tool の実行時引数ではない。公開 tool は sidecar server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で制御する。

## 検証

template と schema の整合性は次で確認する。

```powershell
uv run --with pyyaml --with jsonschema python scripts\validate_precision_templates.py
```

この検証では次を確認する。

- `model_spec.yaml` が `model_spec.schema.json` に一致する
- `addon_registry.yaml` が `addon_registry.schema.json` に一致する
- `validation_report.example.json` が `validation_report.schema.json` に一致する
- `codex_config.toml` に `mcp_servers.blender_precision` と基本 timeout / disabled tool が含まれる
