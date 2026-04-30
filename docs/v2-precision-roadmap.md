# v2 精密モデリング完成ロードマップ

## 1. 目的

v2 では、公式 Blender MCP を土台に、Codex から高品質な Blender モデル制作、検証、視覚レビュー、承認済み add-on 活用を行うための実装基盤を整える。

利用者の自然言語指示は Codex App から行い、Blender 側は公式 `MCP` add-on の接続先として扱う。

## 2. 重要前提

- Codex の STDIO MCP 設定における `command` / `args` は MCP server プロセス起動用である
- tool の公開可否は MCP server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で制御する
- `args` では sidecar MCP server へ profile / config / tool pack を渡し、server 側が公開 tool を切り替える
- MCP tool の実行時引数は `tools/call` の `arguments` で受け取る
- Blender operator は context 依存になりやすいため、`bpy.ops` / `bpy.context` / operator context override は add-on integration の専用責務として扱う

## 3. 完成状態

v2 完成時点で、利用者は次を実行できる。

- installer から公式 Blender MCP と precision profile / Skill / template を導入できる
- Codex App から `blender-precision-mcp` を MCP server として登録できる
- profile / tool pack に応じて公開 tool が切り替わる
- `model_spec.yaml` を使って制作意図、寸法、構成要素、材質、検証条件を明文化できる
- モデル生成後に validation report と review screenshot を保存できる
- 承認済み add-on だけを registry 経由で安全に利用できる

## 4. フェーズ

### Phase v2-0: docs 統合と Issue 分解

- v2 資料を `requirements`, `specification`, `design`, `roadmap`, `validation-plan` へ統合する
- 完成までの実装単位を GitHub Issue として起票する
- `docs/tmp` は設計ソースとして扱い、利用者が読む正式 docs は canonical docs に寄せる

### Phase v2-1: template / schema 正式配置

- `blender_precision_config.yaml`, `model_spec.yaml`, Codex MCP 設定例を正式配置する
- `model_spec`, `validation_report`, `addon_registry` の schema を正式配置する
- 配置先、編集対象、利用者向け説明を docs に反映する

### Phase v2-2: sidecar MCP server scaffold

- `blender-precision-mcp` の server scaffold を追加する
- config / profile / tool pack / policy の読み込みを実装する
- `tools/list` で profile / tool pack に応じた公開 tool を返す
- 危険 tool を policy と Codex `disabled_tools` の両方で抑止する

### Phase v2-3: model spec と validation

- `model_spec.yaml` を読み込み、制作対象、寸法、パーツ、材質、検証条件へ展開する
- scene / mesh / material validation を実装する
- `validation_report` を structured result とファイル出力の両方で残す
- 失敗時に修正候補を返す
- Blender live scene の実測値と spec の差分を検証する

### Phase v2-4: visual QA

- 指定ビューの screenshot を保存する
- front / side / top / perspective などの標準ビューを定義する
- review screenshot と validation report を同じ解析ディレクトリに保存する
- blank check / bounding box check などの最低限の自動判定を行う
- 人が確認するレビュー観点を docs と Skill に反映する

### Phase v2-5: add-on registry / approved operator

- 導入済み add-on と operator capability を調査する
- approved add-on registry を導入する
- `poll`, context, mode, selection, active object, area override を確認する
- modal / UI 専用 operator は structured failure として扱う
- 破壊的 operator は `dry_run -> confirm -> backup -> execute` の順に限定する

### Phase v2-6: Skill / AGENTS / subagent 配布

- 高品質モデリング用 Skill を正式配置する
- Blender add-on 開発用 Skill と分離する
- scene validator、visual reviewer、addon auditor の subagent template を配布する
- 利用者向け導入手順と Codex App 再起動手順を docs に記載する

### Phase v2-7: installer / release

- installer で precision profile / Skill / template の導入を選べるようにする
- 導入後の Finish 操作と次の確認手順を表示する
- release checklist に v2 検証項目を追加する
- examples と validation evidence を release docs に残す
- headless / plan mode では `--include-precision-profile` で任意導入 step を追跡する

## 5. 実装タスクの管理

v2 の残タスクは、現在の実装との差分を GitHub Issue として管理する。完了済み Issue ではなく、現時点で不足している実装を新しい Issue として起票する。

現在の実装待ち Issue:

1. [#106 v2 precision: model_spec から scene を生成・更新する tool 群を実装する](https://github.com/Sunmax0731/blender-mcp/issues/106)
2. [#107 v2 precision: mesh quality report と mesh cleanup tool を実装する](https://github.com/Sunmax0731/blender-mcp/issues/107)
3. [#108 v2 precision: export_scene と成果物 manifest を実装する](https://github.com/Sunmax0731/blender-mcp/issues/108)
4. [#109 v2 precision: blender-precision-mcp の配布方式と installer 登録を確定する](https://github.com/Sunmax0731/blender-mcp/issues/109)
5. [#110 v2 precision: 公式 Blender MCP Example と precision workflow の統合 smoke を追加する](https://github.com/Sunmax0731/blender-mcp/issues/110)

## 6. 判断保留項目

### sidecar 配布方法

- 案A: `blender-precision-mcp` を本リポジトリの package として配布する
- 案B: standalone `uvx` package として公開する
- 案C: installer が local script / venv を生成して登録する

推奨案は A。公式導入補助リポジトリとして管理しやすく、v2 初期の利用者にも説明しやすい。

### add-on execution 初期状態

- 案A: inspection のみ有効
- 案B: approved registry + confirm + backup を満たした operator のみ有効
- 案C: 利用者確認があれば任意 operator を許可

推奨案は B。品質向上に使える一方、未承認 operator と確認なし実行を避けられる。
