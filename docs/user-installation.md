# 利用者向け導入手順

## 1. 対象

この手順は、Windows で Blender 5.1 系と Codex App を使う利用者向けです。

このリポジトリの installer は、公式 Blender MCP を導入し、Codex App から Blender を操作できる状態を作ります。Blender 本体と Codex App 本体は事前にインストールしてください。

## 2. 事前準備

- Windows を利用している
- Blender 5.1 系をインストール済み
- Codex App をインストール済み
- インターネット接続がある
- Blender の `Online Access` を有効にできる
- Codex App を再起動できる

## 3. 推奨導入: installer を使う

1. GitHub Release から `blender-mcp-installer.exe` をダウンロードする
2. `blender-mcp-installer.exe` を実行する
3. 画面に表示される変更対象を確認する
4. 確認チェックを有効にする
5. 必要な場合だけ precision profile のチェックを有効にする
6. `Start Install` を押す
7. ログに失敗がないことを確認する
8. 導入完了後、`Finish` を押して installer を閉じる
9. Codex App を再起動する
10. Blender を起動する

installer は次を順番に実行します。

- 公式 Blender MCP add-on の導入
- 公式 Blender MCP server の導入
- Codex App への `blender-official` MCP server 登録
- Blender 側の公式 `mcp` add-on 有効化
- 不要な補助 UI 登録の cleanup
- 任意で precision profile、Skill、subagent template、`blender_precision` MCP server の導入

## 4. 任意導入: precision profile

precision profile は、高品質モデリング支援のための optional experimental 機能です。

通常の公式 Blender MCP 導入だけを使う場合は有効にする必要はありません。導入すると、Codex 用 template、Skill、subagent template に加えて、installer-managed venv で起動する `blender_precision` MCP server が Codex App に登録されます。

precision profile 導入時は、既存の Codex `config.toml` を丸ごと置き換えません。既存 file をバックアップし、installer が生成した `[mcp_servers.blender_precision]` section を更新します。過去の `uvx` 前提の experimental section が残っている場合も、バックアップ後に現在の起動方式へ置き換えます。

headless で導入する場合:

```powershell
uv run blender-mcp-installer --headless --include-precision-profile
```

precision profile の config 追記予定だけ確認する場合:

```powershell
.\scripts\install_precision_profile.ps1 -PlanConfigMerge
```

## 5. 導入後の確認

Blender 側:

1. Blender を起動する
2. `Edit > Preferences > Add-ons` または `Get Extensions` を開く
3. `MCP` が導入済みで有効になっていることを確認する
4. Blender の `Online Access` が有効であることを確認する
5. add-on 設定で host / port / autostart を確認する

Codex App 側:

1. Codex App を再起動する
2. `blender-official` MCP server が利用できることを確認する
3. precision profile を導入した場合は `blender_precision` MCP server が利用できることを確認する
4. Blender を起動した状態で、状態取得や screenshot 取得を試す

## 6. headless / plan mode

実行予定だけ確認する場合:

```powershell
uv run blender-mcp-installer --plan
```

GUI を使わず導入する場合:

```powershell
uv run blender-mcp-installer --headless
```

最後の Blender 起動を抑止する場合:

```powershell
uv run blender-mcp-installer --headless --no-launch-blender
```

ログを保存する場所を指定する場合:

```powershell
uv run blender-mcp-installer --headless --output-dir <log-dir>
```

## 7. 更新・再導入

同じ環境で再導入する場合も、まず `--plan` で変更予定を確認してください。

Codex App の設定変更後は Codex App の再起動が必要です。Blender 側の add-on 設定を変更した場合は、Blender の再起動または add-on の再有効化を行ってください。
