# v1.0.0 release scope

## 1. Release 方針

`v1.0.0` は、このリポジトリの正式 Release として扱う。

正式 Release の主対象は、Windows 利用者が公式 Blender MCP を導入し、Codex App から Blender を操作できる状態にすることである。配布物の中心は `blender-mcp-installer.exe` とし、公式 Blender MCP 本体、Blender 本体、Codex App 本体はこのリポジトリの Release asset として再配布しない。

v2 precision profile は optional experimental として扱う。

## 2. 版数の扱い

- このリポジトリの正式 Release: `blender-mcp v1.0.0`
- 対応する公式 Blender MCP: `official blender_mcp v1.0.0`
- GitHub tag / Release 名称: `v1.0.0`

公式 Blender MCP の版数と、このリポジトリの installer / docs / integration の版数は分けて扱う。

## 3. v1.0.0 に含めるもの

### 3.1 正式機能

- Windows 向け 1クリック導入アプリ
- 公式 Blender MCP add-on の導入
- 公式 Blender MCP server の専用仮想環境への導入
- Codex App 用 `blender-official` MCP server 登録
- Blender 側の公式 `mcp` add-on 有効化
- 導入ログ保存
- 導入完了後の明示的な `Finish` 操作
- GUI / headless / plan mode
- 利用者向け導入手順書
- 利用者向け利用方法
- 機能説明
- トラブルシュート

### 3.2 optional experimental

- precision profile template
- `blender-precision-mcp` sidecar scaffold
- profile / tool-pack による tool 公開制御
- `model_spec` / `validation_report` / `addon_registry` schema
- dry-run / static validation
- visual QA manifest
- add-on registry inspection
- approved operator dry-run safety gate
- precision Skill / AGENTS / subagent template
- installer の `--include-precision-profile`

## 4. v1.0.0 に含めないもの

- Blender 本体の自動インストール
- Codex App 本体の自動インストール
- macOS / Linux 向け installer
- 公式 Blender MCP 本体の fork / 改造
- 公式 Blender MCP zip の Release asset としての再配布
- 外部公開前提の常駐 server 構成
- 任意 Python / `bpy` 実行の通常導線での許可
- Blender 側から Codex を直接呼び出す独自操作導線
- v2 precision の全 tool 実装完了保証
- Blender live scene の完全自動品質保証
- 任意 add-on operator の無制限実行

## 5. Blocker / Non-blocker

### 5.1 Blocker

- installer が起動しない
- plan mode が失敗する
- Codex 設定を壊し、復旧手順がない
- 公式 Blender MCP add-on の導入または有効化が再現できない
- Release asset を取得できない
- checksum が一致しない
- README から導入手順に到達できない
- 利用者向け docs に重大な誤記、文字化け、環境依存の絶対パスが残っている
- known limitations が Release notes に明記されていない

### 5.2 Non-blocker

- v2 precision の live scene validation 完成
- visual QA の画像差分の自動判定
- approved add-on operator の live integration
- macOS / Linux 対応
- Blender / Codex App 本体の自動導入

Non-blocker は Release 後 follow-up Issue として管理する。

## 6. Go 条件

- P0 / P1 の未解決 blocker がない
- `uv run pytest` が成功している
- `uv run blender-mcp-installer --plan` が成功している
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender` が成功している
- installer exe、checksum、manifest が作成されている
- Release asset の download / hash 検証が完了している
- Blender 5.1 系で公式 `MCP` add-on 導入 / 有効化の証跡がある
- Codex App から公式 Blender MCP tool の live 接続証跡がある
- 導入手順書、利用方法、機能説明、トラブルシュートが公開されている

## 7. No-Go 条件

- installer または plan mode が起動できない
- Codex 設定変更の安全性を説明できない
- Release asset に不要な再配布物や検証 artifact が混入している
- Release notes と docs の既知制約が一致しない
- 利用者向け docs が未整備
- live validation 未実施かつ代替判断材料が Issue に残っていない

## 8. 推奨判断

v1.0.0 では、公式 Blender MCP 導入と Codex / Blender 接続導線を正式機能とする。v2 precision は optional experimental として同梱し、Release notes と利用者向け docs で明示する。
