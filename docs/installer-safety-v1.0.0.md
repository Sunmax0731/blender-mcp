# v1.0.0 installer safety checklist

## 1. 目的

`v1.0.0` 正式 Release では、installer が何を変更するかを利用者が理解し、失敗時に確認できる状態にする。

## 2. 利用者に見せる変更対象

installer は次を変更する。

- Blender の公式 `mcp` add-on
- 公式 Blender MCP server 用の専用仮想環境
- Codex App の MCP server 設定
- 任意導入時のみ precision profile template / Skill / subagent

installer は次をインストールしない。

- Blender 本体
- Codex App 本体
- macOS / Linux 向け構成
- 公式 Blender MCP zip の Release asset 再配布

## 3. GUI の確認ポイント

- 導入前に変更対象が表示される
- 確認チェックを有効にするまで導入開始できない
- 導入中は step と log が表示される
- 導入成功後に `Finish` が有効になる
- 導入失敗時は `Finish` を有効にせず、log で失敗 step を確認できる

## 4. headless / plan mode

実行予定だけ確認する:

```powershell
uv run blender-mcp-installer --plan
```

precision profile を含む予定を確認する:

```powershell
uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender
```

GUI を使わず実行する:

```powershell
uv run blender-mcp-installer --headless
```

ログ保存先を指定する:

```powershell
uv run blender-mcp-installer --headless --output-dir <log-dir>
```

## 5. Codex config safety

通常の公式 Blender MCP 登録では、既存 `config.toml` をバックアップしてから `blender-official` を登録する。

precision profile 導入では、既存 `config.toml` を丸ごと置き換えない。`mcp_servers.blender_precision` が未登録の場合だけ、バックアップを作成したうえで precision 用 block を追記する。

precision profile の config 追記予定だけ確認する:

```powershell
.\scripts\install_precision_profile.ps1 -PlanConfigMerge
```

## 6. Release 前に確認すること

- `uv run pytest`
- `uv run blender-mcp-installer --plan`
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender`
- GUI 起動時に `Finish` が無効である
- GUI 導入成功後に `Finish` が有効になる
- precision profile の `-PlanConfigMerge` が config を変更しない
- precision profile の `-MergeCodexConfig` が backup を作成して追記する

## 7. 失敗時の確認順

1. installer log の `[FAILED]` step を確認する
2. Blender がインストール済みか確認する
3. Blender の `Online Access` を確認する
4. Codex App を再起動したか確認する
5. `--plan` で予定 step が表示されるか確認する
6. `config.toml.backup-<timestamp>` がある場合は差分を確認する
