# blender-mcp v0.1.0

Windows 環境で、Blender 5.1 系と Codex App を前提に、公式 Blender MCP を導入しやすくする初回 Release です。

主配布物は `blender-mcp-installer.exe` です。公式 Blender MCP 本体はこのリポジトリの Release asset として再配布せず、導入時に公式配布物を取得します。

## 含まれるもの

### 1クリック導入アプリ

- Codex への `blender-official` MCP server 登録
- Blender への公式 `mcp` add-on 導入
- 公式 `mcp` add-on の有効化
- 導入ログの保存
- 導入完了後の `Finish` 操作
- `--plan` / `--headless` / `--no-launch-blender`

### 任意導入: v2 precision profile foundation

`--include-precision-profile` または GUI の任意チェックで、次を追加導入できます。

- precision template / schema
- `blender-precision-mcp` sidecar scaffold
- profile / tool-pack による tool 公開制御
- `model_spec` / `validation_report` / `addon_registry`
- dry-run / static validation
- visual QA manifest
- add-on registry inspection
- approved operator dry-run safety gate
- precision Skill / AGENTS / subagent template

v2 precision は初期 foundation として含めます。全 tool 実装完了版ではありません。

## 前提条件

- Windows
- Blender 5.1 系がインストール済み
- Codex App がインストール済み
- ネットワーク接続があり、公式 Blender MCP 配布物を取得できる
- ローカルの Codex 設定変更を許可できる

## セットアップ

1. GitHub Release から `blender-mcp-installer.exe` を取得する
2. `blender-mcp-installer.exe` を実行する
3. 変更対象の説明を確認する
4. 確認チェックを有効にして導入を開始する
5. 導入完了後、`Finish` で installer を閉じる
6. Codex App を再起動する
7. Blender で `Edit > Preferences > Get Extensions` を開き、`MCP` が有効であることを確認する

precision profile を任意導入する場合:

```powershell
uv run blender-mcp-installer --headless --include-precision-profile
```

## 動作確認対象

Release 前に次を確認します。

- `uv run pytest`
- `uv run blender-mcp-installer --plan`
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender`
- precision template / schema validation
- installer exe rebuild
- checksum / packaging manifest
- Blender 5.1 での公式 `MCP` add-on 導入 / 有効化
- Codex App からの公式 Blender MCP live 接続
- Blender UI Prompt の `Plan -> Confirm -> Execute`

## GitHub Release に添付するもの

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v0.1.0.json`

## GitHub Release に添付しないもの

- 公式 Blender MCP zip
- Blender 本体
- Codex App 本体
- Python 仮想環境
- 検証 artifact 一式

## 既知制約

- Blender 本体と Codex App 本体の自動インストールは行いません
- macOS / Linux 向け配布は含みません
- 公式 Blender MCP 本体はこの Release で fork や再配布を行いません
- live 接続確認は Blender 起動状態に依存します
- v2 precision の一部 tool は初期実装であり、structured `not_implemented` を返します
- visual QA の実 screenshot 保存は Blender Python 内で実行する必要があります
- add-on operator の実実行は Blender Python と対象 add-on が導入済みの環境で検証する必要があります
- precision profile installer は Codex home へ template / Skill / subagent をコピーします。既存 `config.toml` への自動マージは行いません

## 関連ドキュメント

- [v0.1.0 setup checklist](setup-checklist-v0.1.0.md)
- [v0.1.0 release scope](release-scope-v0.1.0.md)
- [v0.1.0 release assets](release-assets-v0.1.0.md)
- [v2 release validation](release-validation-v2.md)
- [Release milestone plan](release-milestones.md)
