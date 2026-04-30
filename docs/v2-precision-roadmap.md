# v2 精密モデリング完成ロードマップ

## 1. 目的

v2 では、公式 Blender MCP を土台に、Codex から高品質な Blender モデル制作、検証、視覚レビュー、承認済み add-on 活用を行うための実装基盤を整える。

この段階では、`docs/tmp` に配置された v2 資料をそのまま正式仕様にするのではなく、既存 docs と Issue に統合し、実装・検証・配布の順で完成へ進める。

## 2. 重要前提

- Codex の STDIO MCP 設定における `command` / `args` は MCP server プロセス起動用である
- tool の公開可否は MCP server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で制御する
- `args` では sidecar MCP server へ profile / config / tool pack を渡し、server 側が公開 tool を切り替える
- MCP tool の実行時引数は `tools/call` の `arguments` で受け取る
- BlenderMCP は Blender add-on と MCP server の 2 要素で構成される
- Blender operator は context 依存になりやすいため、`bpy.ops` / `bpy.context` / operator context override は add-on integration の専用設計として扱う

## 3. 完成状態

v2 完成時点で、利用者は次を実行できる状態を目指す。

- installer から公式 Blender MCP と precision profile / Skill / template を導入できる
- Codex App / Codex CLI から `blender-precision-mcp` を MCP server として登録できる
- profile / tool pack に応じて公開 tool が切り替わる
- `model_spec.yaml` を使って制作意図と検証条件を明文化できる
- モデル生成後に validation report と review screenshot を保存できる
- 承認済み add-on だけを registry 経由で安全に利用できる
- Blender UI から prompt、preview、confirm、execute の導線でモデル制作を開始できる

## 4. フェーズ

### Phase v2-0: docs 統合と Issue 分解

- v2 資料の要点を `requirements`, `specification`, `design`, `roadmap`, `validation-plan` へ統合する
- 完成までの実装単位を GitHub Issue として起票する
- tmp 資料は設計ソースとして扱い、利用者が読む正式 docs は canonical docs に寄せる

### Phase v2-1: template / schema 正式配置

- `blender_precision_config.yaml`、`model_spec.yaml`、Codex MCP 設定例を正式配置する
- `model_spec`, `validation_report`, `addon_registry` の schema を正式配置する
- 配置先、編集対象、利用者向け説明を docs に反映する
- 正式配置先は [v2 precision template / schema](precision-templates.md) に記載する

### Phase v2-2: sidecar MCP server scaffold

- `blender-precision-mcp` の server scaffold を追加する
- config、profile、tool pack、policy の読み込みを実装する
- `tools/list` で profile / tool pack に応じた公開 tool を返す
- 危険 tool を policy と Codex `disabled_tools` の両方で抑止する
- 最小 scaffold は `blender-precision-mcp --dry-run` で設定解決を確認できる

### Phase v2-2.5: profile / tool-pack tools/list 制御

- sidecar の control tool は常に公開する
- profile / tool-pack 由来の tool は policy block を通過したものだけ公開する
- 未実装 tool は structured `not_implemented` を返し、後続 Issue で実処理を追加する

### Phase v2-3: model spec と validation

- `model_spec.yaml` を読み込み、制作対象、寸法、パーツ、材質、検証条件へ展開する
- scene / mesh / material validation を実装する
- `validation_report` を structured result とファイル出力の両方で残す
- 失敗時に修正候補を返す
- 初期実装では Blender live 接続に依存しない schema / static validation を先に提供し、scene 実測値との差分検証は後続で拡張する

### Phase v2-4: visual QA

- 指定ビューの viewport screenshot を保存する
- 正面、側面、俯瞰、材質確認などの標準ビューを定義する
- review screenshot と validation report を同じ成果物ディレクトリに保存する
- 人が確認するレビュー観点を docs と Skill に反映する
- `scripts/capture_precision_review_views.py` は Blender Python 内では画像を保存し、通常 Python では dry-run manifest を作成する

### Phase v2-5: add-on registry / approved operator

- 導入済み add-on と operator capability を調査する
- approved add-on registry を導入する
- `poll`、context、mode、selection、active object、area override を確認する
- modal / UI 専用 operator は structured failure として扱う
- 破壊的 operator は backup 後にだけ実行する
- `scripts/inspect_precision_addons.py` で registry と導入済み add-on 状態を確認する
- approved operator wrapper は registry、context、poll、backup policy を通過した operator だけを実行対象にする

### Phase v2-6: Blender UI prompt flow 統合

- Blender UI から prompt を入力できる補助パネルを実装する
- Codex CLI に plan を作らせ、preview / confirm / execute を経て実行する
- 実行結果、validation report、review screenshot の場所を UI で確認できる
- 公式 `mcp` add-on の設定や責務を上書きしない
- 既存補助 add-on は `Plan -> Confirm -> Execute` の明示ボタンを持ち、互換用の旧 `send_prompt` operator は維持する

### Phase v2-7: Skill / AGENTS / subagent 配布

- 高品質モデリング用 Skill を正式配置する
- Blender add-on 開発用 Skill と分離する
- scene validator、visual reviewer、addon auditor の subagent template を配布する
- 利用者向け導入手順と再起動手順を docs に記載する
- v2 precision 用の `AGENTS.md` / `SKILL.md` / subagent template は `templates/precision/` を正式配布元にする

### Phase v2-8: installer / release

- installer で precision profile / Skill / template の導入を選べるようにする
- 導入後の Finish 操作と次の確認手順を表示する
- release checklist に v2 検証項目を追加する
- examples と validation evidence を release docs に残す

## 5. 完成までの Issue 分解

v2 完成までのタスクは、1 Issue で完結できる単位に分ける。

1. [#62 template / schema 正式配置](https://github.com/Sunmax0731/blender-mcp/issues/62)
2. [#63 sidecar MCP server scaffold](https://github.com/Sunmax0731/blender-mcp/issues/63)
3. [#64 profile / tool-pack による `tools/list` 制御](https://github.com/Sunmax0731/blender-mcp/issues/64)
4. [#65 `model_spec` 読み込みと validation report](https://github.com/Sunmax0731/blender-mcp/issues/65)
5. [#66 viewport screenshot と visual QA](https://github.com/Sunmax0731/blender-mcp/issues/66)
6. [#67 add-on registry と inspection workflow](https://github.com/Sunmax0731/blender-mcp/issues/67)
7. [#68 approved operator execution と context preparation](https://github.com/Sunmax0731/blender-mcp/issues/68)
8. [#69 Blender UI prompt flow 実装](https://github.com/Sunmax0731/blender-mcp/issues/69)
9. [#70 Skill / AGENTS / subagent template 配布](https://github.com/Sunmax0731/blender-mcp/issues/70)
10. [#71 installer の precision profile 導入対応](https://github.com/Sunmax0731/blender-mcp/issues/71)
11. [#72 v2 release validation と examples 整備](https://github.com/Sunmax0731/blender-mcp/issues/72)

## 6. 判断保留項目

### sidecar 実装パッケージ名

- 候補 A: `blender-precision-mcp`
- 候補 B: `blender-mcp-sidecar`
- 候補 C: `codex-blender-precision`

推奨案は A。利用者に目的が伝わりやすく、v2 の precision modeling という目的と一致する。

### template 正式配置先

- 候補 A: `templates/precision/`
- 候補 B: `docs/templates/`
- 候補 C: `.agents/` と `.codex/` を repo root に直接配置

推奨案は A。配布物として扱いやすく、docs と実行時設定を混在させずに済む。

### add-on execution 初期状態

- 候補 A: 無効。inspection だけ有効
- 候補 B: approved registry がある operator だけ有効
- 候補 C: 利用者確認があれば任意 operator を実行可能

推奨案は A。v2 初期は registry と context preparation の精度を固める段階であり、実行は明示的な追加 Issue で有効化する。
