# v0.1.0 release scope

## 1. Release 方針

v0.1.0 は、Windows 利用者が公式 Blender MCP を導入し、Codex App から Blender を操作するための初回 Release とする。

主配布物は `blender-mcp-installer.exe` である。v2 precision profile は、完成済みの高機能モデリング環境としてではなく、任意導入できる初期 foundation として含める。

## 2. 含めるもの

### 2.1 主導線

- 1 クリック導入アプリ
- 公式 Blender MCP add-on 導入補助
- 公式 Blender MCP server 専用仮想環境導入
- Codex App 用 `blender-official` MCP server 登録
- Blender 側の公式 `mcp` add-on 有効化
- 導入ログ保存
- 導入完了後の Finish 操作

### 2.2 任意導線

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

## 3. 含めないもの

- Blender 本体の自動インストール
- Codex App 本体の自動インストール
- macOS / Linux 向け配布物
- 公式 Blender MCP 本体の fork 改造
- 公式 Blender MCP zip の GitHub Release asset としての再配布
- 公開ネットワーク前提の常設 server 構成
- 任意 Python / `bpy` 実行の通常導線での許可
- v2 precision の全 tool 実装完了保証
- Blender live scene の全自動品質保証
- 任意 add-on operator 実行

## 4. Go 条件

- P0 / P1 の未解決不具合がない
- `uv run pytest` が成功している
- `uv run blender-mcp-installer --plan` が成功している
- `uv run blender-mcp-installer --plan --include-precision-profile --no-launch-blender` が成功している
- precision template / schema validation が成功している
- installer exe を再ビルドし、checksum を記録している
- Blender 5.1 で公式 `MCP` add-on 導入 / 有効化の証跡がある
- Codex App から公式 Blender MCP tool の live 接続証跡がある
- Release notes に known limitations が明記されている

## 5. No-Go 条件

- installer が起動しない、または plan mode が失敗する
- Codex 設定登録が壊れ、復旧手順がない
- 公式 Blender MCP add-on 有効化が再現できない
- Release asset に公式 Blender MCP zip、仮想環境、検証 artifact が混入している
- known limitations に未記載の重大制約がある
- live validation が未完了で、manual bypass の判断材料もない

## 6. P0 / P1 の扱い

- P0: 導入不能、設定破壊、Release asset 取得不能、復旧不能な破壊的操作。Release 前に必ず修正する
- P1: 主導線の失敗、検証証跡不足、docs と実装の不一致。Release 前に修正または明示的な No-Go 解除判断を Issue に残す
- P2 以降: Release 後 follow-up Issue として分離できる

## 7. v2 precision の公開表現

v2 precision は「任意導入できる初期 foundation」として表現する。Release notes では、次を明記する。

- 一部 tool は structured `not_implemented` を返す
- Blender Python 内でないと実 screenshot / add-on operator 実行はできない
- `config.toml` の自動マージは行わず、template 配布に留める
- full workflow は今後の milestone で拡張する
