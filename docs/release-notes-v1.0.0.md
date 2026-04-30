# blender-mcp v1.0.0

Windows 環境で、Blender 5.1 系と Codex App を前提に、公式 Blender MCP を導入・利用しやすくする正式 Release です。

主配布物は `blender-mcp-installer.exe` です。公式 Blender MCP 本体、Blender 本体、Codex App 本体はこの Release asset として再配布しません。

## 含まれるもの

### 正式機能

- Windows 向け 1クリック導入アプリ
- 公式 Blender MCP add-on の導入
- 公式 Blender MCP server の専用仮想環境への導入
- Codex App への `blender-official` MCP server 登録
- Blender 側の公式 `mcp` add-on 有効化
- 導入ログ表示
- 導入完了後の `Finish` 操作
- `--plan` / `--headless` / `--no-launch-blender`
- 利用者向け導入手順
- 利用者向け利用方法
- 機能説明
- トラブルシュート

### optional experimental

v2 precision profile foundation は任意導入の experimental 機能として同梱します。

- precision template / schema
- `blender-precision-mcp` sidecar scaffold
- profile / tool-pack による tool 公開制御
- `model_spec` / `validation_report` / `addon_registry`
- dry-run / static validation
- visual QA manifest
- add-on registry inspection
- approved operator dry-run safety gate
- precision Skill / AGENTS / subagent template
- 既存 Codex `config.toml` への安全な追記

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

## 動作確認

Release 前に次を確認しました。

- `uv run pytest`
- `uv run blender-mcp-installer --plan`
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender`
- installer exe rebuild
- checksum / packaging manifest
- precision profile の config merge / backup
- Blender 5.1 での公式 `MCP` add-on 導入 / 有効化
- Codex App からの公式 Blender MCP live 接続
- 3D View screenshot 取得

## GitHub Release に添付するもの

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v1.0.0.json`

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
- v2 precision は optional experimental です
- v2 precision の live scene validation、visual QA、approved add-on operator integration は post-v1 の拡張タスクです

## 関連ドキュメント

- [利用者向け導入手順](https://github.com/Sunmax0731/blender-mcp/blob/v1.0.0/docs/user-installation.md)
- [利用者向け利用方法](https://github.com/Sunmax0731/blender-mcp/blob/v1.0.0/docs/user-guide.md)
- [機能説明](https://github.com/Sunmax0731/blender-mcp/blob/v1.0.0/docs/features.md)
- [トラブルシュート](https://github.com/Sunmax0731/blender-mcp/blob/v1.0.0/docs/troubleshooting.md)
- [v1.0.0 release scope](https://github.com/Sunmax0731/blender-mcp/blob/v1.0.0/docs/release-scope-v1.0.0.md)
- [v1.0.0 release manifest](https://github.com/Sunmax0731/blender-mcp/blob/v1.0.0/docs/release-manifest-v1.0.0.md)
