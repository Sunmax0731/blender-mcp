# v0.1.0 setup checklist

## 1. 対象利用者

Windows PC に Blender 5.1 系と Codex App を導入済みの利用者を対象にする。

この Release は Blender 本体と Codex App 本体を自動インストールしない。

## 2. 導入前に確認すること

- Windows 環境である
- Blender 5.1 系を起動できる
- Codex App を起動できる
- ネットワーク接続がある
- ローカルの Codex 設定変更を許可できる

## 3. 通常導入

1. GitHub Release から `blender-mcp-installer.exe` を取得する
2. `blender-mcp-installer.exe` を実行する
3. 変更対象の説明を確認する
4. 確認チェックを有効にして導入を開始する
5. 導入完了後、`Finish` で installer を閉じる
6. Codex App を再起動する
7. Blender を起動し、`Edit > Preferences > Get Extensions` で `MCP` が有効であることを確認する

## 4. 任意導入: precision profile

v2 precision profile は任意導入である。通常の公式 Blender MCP 導入だけを使う場合は有効にしなくてよい。

precision profile を導入すると、Codex 用の template、Skill、subagent template が Codex home 配下にコピーされる。既存の `config.toml` へ自動マージは行わない。

## 5. 導入後の確認

Blender 側:

- `MCP` が有効になっている
- Blender の `Online Access` が有効になっている
- host / port / autostart を確認できる

Codex App 側:

- Codex App 再起動後に `blender-official` MCP server が利用できる
- Blender 起動状態で screenshot または scene inspection 系 tool を試せる

## 6. 困ったとき

- Codex App 側に MCP server が見えない場合は、Codex App を再起動する
- Blender 側で `MCP` が起動しない場合は、`Online Access` を確認する
- 導入に失敗した場合は installer のログを確認する
- precision profile は任意機能のため、通常導入の問題切り分け時はいったん無効にしてよい
