# 仕様

## 1. 前提

- 対象 Blender: 5.1 系
- 公式 Blender MCP: `v1.0.0` を初期基準とする
- OS: Windows
- Python 環境: 3.11 系
- パッケージ管理: `uv`

## 2. 公式配布物

### 2.1 add-on / extension 配布物

- リリース資産: `mcp-1.0.0.zip`
- 配置対象: Blender add-on / extension
- 確認済み主要ファイル:
  - `blender_manifest.toml`
  - `__init__.py`
  - `cli.py`
  - `mcp_to_blender_server.py`

### 2.2 リリース版数

- 2026-04-30 時点で確認した初期対応版: `v1.0.0`

## 3. 本リポジトリが提供するもの

### 3.1 導入スクリプト

- 公式 `mcp-1.0.0.zip` を取得する
- ローカル展開して Blender add-on 配置先へ同期する
- 将来的にバージョン指定更新へ対応できる構造にする
- 公式 MCP server はリポジトリルート直下の専用仮想環境 `.official-mcp-venv/` へ導入する
- Codex App 用の MCP 設定登録スクリプトを提供する

### 3.1.1 Blender 側の前提

- `Edit > Preferences > Get Extensions` で `MCP` を確認し有効化する
- Blender の `Online Access` を有効化する
- host / port / autostart は add-on 設定に従う
- 背景実行では `--online-mode` が必要になる
- Blender 実行パスは `BLENDER_PATH` で明示できるが、Codex 起動スクリプト側でも自動解決する

### 3.2 ドキュメント

- 公式構成の説明
- Codex App からの利用前提
- Blender 側の確認対象を公式 `MCP` add-on Preferences に限定すること
- 更新と検証の運用手順

### 3.3 補助機能

- 旧開発版の不要な add-on 登録を削除する補助スクリプト
- 公式構成で不足する運用自動化

### 3.4 1クリック導入アプリ

- 単一の GUI エントリポイントから導入フローを開始できる
- 内部では既存 PowerShell スクリプトを順次呼び出す
- 実行結果、失敗箇所、再実行可否を UI 上で利用者へ示す

## 4. 1クリック導入アプリ仕様

### 4.1 起動前確認

- Blender 実行ファイルの探索
- Codex 設定ファイルの存在確認
- add-on 配置先の解決
- ネットワーク接続前提の注意表示

### 4.2 実行ステップ

1. 公式 add-on 配布物を取得する
2. Blender add-on 配置先へ導入する
3. 公式 MCP server を専用仮想環境へ導入する
4. Codex 設定へ `mcp_servers.blender-official` を登録する
5. Blender 側で公式 `mcp` を有効化する
6. 旧開発版の不要な add-on 登録が残っていれば削除する
7. 導入後の確認項目を表示する

### 4.3 UI 要素

- 実行開始ボタン
- 現在ステップの進捗表示
- 実行ログ表示領域
- 完了後の確認項目表示
- 失敗時の再実行案内

### 4.4 ログと証跡

- 実行ログをローカルファイルへ保存する
- UI 上でも直近ログを参照できる
- 失敗したステップ名と例外メッセージを保持する
- 再実行時に前回ログを消さず追記または別名保存する

### 4.5 確認フロー

- 既存 Codex 設定の変更前に、変更対象ファイルとバックアップ作成を利用者へ示す
- Blender 側の設定変更前に、何を切り替えるかを利用者へ示す
- 危険操作は `preview -> confirm -> execute` を守る

## 5. 独自構成の扱い

- 既存独自 add-on / server は移行中資産とする
- 新規主経路としては扱わない
- 公式移行が完了するまで、比較・参考・退避対象として保持する

## 6. Blender 側の扱い

Blender 側では、公式 `MCP` add-on の Preferences を確認対象とする。
利用者が Blender 側で確認する画面は、公式 `MCP` add-on の Preferences とする。

### 6.1 cleanup 対象

- 旧 `blender_mcp` add-on の Preferences 登録
- 旧開発版 module がユーザー add-on 配下に残っている場合の退避

### 6.2 cleanup 非対象

- 公式 `bl_ext.user_default.mcp`
- 公式 `mcp` extension directory
- Blender 本体設定のうち、公式 add-on と無関係な項目

## 7. 検証観点

- 公式配布物が取得できること
- Blender へ導入できること
- Blender 側で add-on が有効化できること
- 公式 `mcp` が主経路として有効化されること
- 公式 MCP server が専用仮想環境へ導入できること
- Codex 設定へ `mcp_servers.blender-official` を登録できること
- 公式構成を前提に docs が一致していること
- 旧開発版の不要な add-on 登録が公式構成を壊さず削除できること
- GUI 導入アプリから実行順序とログが追跡できること
- 利用者向け導線が Codex App と公式 MCP に一本化されていること

## 8. v2 精密モデリング仕様

### 8.1 sidecar MCP server

`blender-precision-mcp` は、公式 Blender MCP server / add-on を直接置き換えず、Codex と公式 Blender MCP の間で高水準 tool、検証、設定制御を担う sidecar / proxy として扱う。

想定起動設定:

- `command`: sidecar MCP server プロセスを起動する実行ファイル
- `args`: `--config`, `--profile`, `--tool-pack` など、server 起動時の設定
- `env` / `cwd`: Blender 接続先、設定ファイル、作業ディレクトリ
- `startup_timeout_sec` / `tool_timeout_sec`: 起動と tool 実行のタイムアウト
- `enabled_tools` / `disabled_tools`: Codex 側での公開 tool 制御

`args` は tool の実行時引数ではない。MCP tool の実行時引数は `tools/call` の `arguments` で受け取る。

### 8.1.1 precision profile 導入後の正常系

- 利用者は installer 完了後、まず `blender-official` で Blender 接続と screenshot 取得を確認する
- その後 `blender_precision` で `model_spec` の dry-run、static validation、config 確認を行う
- `bpy` を必要とする scene 生成、review image 保存、live export は Blender 側実行経路で行う
- sidecar 側で `error.code=blender_unavailable` が返った場合は、Blender background 実行または official MCP scene snapshot 併用を案内する

### 8.2 tool 公開制御

sidecar MCP server は、profile、tool pack、policy、approved add-on registry を読み込み、`tools/list` で公開する tool を切り替える。

代表的な tool pack:

- `modeling`: 形状生成、材質設定、命名、階層整理
- `validation`: scene / mesh / material validation
- `visual_qa`: viewport screenshot、レビュー画像生成、差分確認
- `addon_inspection`: 導入済み add-on、operator、capability の調査
- `addon_execution`: 承認済み add-on operator の実行。初期状態では無効化する

危険 tool は既定で `disabled_tools` または policy block に置く。

### 8.3 データ契約

MCP tool は次を持つ。

- `name`
- `description`
- `inputSchema`
- 任意の `outputSchema`

v2 で標準化する主なデータ:

- `model_spec`: 制作対象、寸法、パーツ、材質、品質基準、検証条件
- `validation_report`: 検証結果、警告、失敗理由、レビュー画像、修正提案
- `addon_registry`: 承認済み add-on、operator、property map、context 条件、破壊的操作フラグ

### 8.3.1 全自動キャラクター生成の schema

`model_spec` の前段として、prompt から内部生成する `character_spec` と、工程間受け渡し用の `pipeline_spec` を定義する。

#### `character_spec`

`character_spec` は、利用者 prompt を 5 要件完全自動のために正規化した論理仕様とする。少なくとも次を持つ。

- `character_type`
  - `humanoid`
  - `chibi`
  - `creature`
- `body_proportions`
  - 頭身
  - 肩幅
  - 胴体長
  - 腕長
  - 脚長
  - 手足サイズ
- `parts`
  - 頭
  - 胴
  - 腕
  - 脚
  - 手
  - 足
  - 髪
  - 衣装主要部位
- `look_spec`
  - 部位別色
  - 模様
  - 材質
  - UV / texture 要件
- `rig_spec`
  - 骨格類型
  - 必須骨一覧
  - 類型別拡張骨
- `expression_spec`
  - 必須表情セット
  - 口形状
  - まばたき
- `pose_test_spec`
  - 基準ポーズ
  - 必須検証ポーズ

初期仕様では、見た目再現に UV と画像テクスチャを含める。

#### `pipeline_spec`

`pipeline_spec` は、`character_spec` を各工程へ落とした実行仕様とする。少なくとも次を持つ。

- `source_prompt`
- `normalized_character_spec`
- `shape_stage`
- `look_stage`
- `rig_stage`
- `expression_stage`
- `weight_stage`
- `validation_plan`
- `artifact_plan`
- `fallback_plan`

各 stage は、最低でも次を含む。

- `inputs`
- `outputs`
- `dependencies`
- `validators`
- `retry_policy`

#### 類型別差分

- `humanoid` は標準的な二足人型骨格と顔表情を前提にする
- `chibi` は短い四肢、強い頭身差、簡略化された手足形状を前提にする
- `creature` は追加肢、尾、非人型頭部などの拡張部位を許容する

類型差分は `character_spec.character_type` によって切り替え、`pipeline_spec` 側では stage ごとのテンプレート選択に変換する。

### 8.3.2 工程 API 契約

5 要件完全自動の工程 API は、少なくとも `dry_run`、`live`、`validation` の 3 種類の呼び出し文脈を区別する。

#### shape_stage

- 入力
  - `character_spec.body_proportions`
  - `character_spec.parts`
  - 類型別 shape template
- 出力
  - mesh object 群
  - shape validation 用 snapshot
- 依存
  - `character_type`
- 再実行条件
  - silhouette failed
  - 部位比率 failed

#### look_stage

- 入力
  - `character_spec.look_spec`
  - UV / texture 要件
  - shape_stage 出力 mesh
- 出力
  - material 設定
  - texture asset
  - look validation 用 review data
- 依存
  - shape_stage
- 再実行条件
  - 色味 failed
  - 模様位置 failed
  - texture / UV 破綻 failed

#### rig_stage

- 入力
  - `character_spec.rig_spec`
  - 類型別 rig template
  - shape_stage 出力 mesh
- 出力
  - armature
  - bone mapping
  - rig validation 用 report
- 依存
  - shape_stage
- 再実行条件
  - 骨命名 failed
  - 親子関係 failed
  - 寸法フィット failed

#### expression_stage

- 入力
  - `character_spec.expression_spec`
  - face topology
  - rig_stage 出力
- 出力
  - shape key 群
  - expression validation 用 preview
- 依存
  - shape_stage
  - rig_stage
- 再実行条件
  - 左右破綻 failed
  - neutral 復帰 failed
  - 表情干渉 failed

#### weight_stage

- 入力
  - `character_spec.pose_test_spec`
  - rig_stage 出力 armature
  - shape_stage 出力 mesh
- 出力
  - weight data
  - pose test report
- 依存
  - shape_stage
  - rig_stage
  - expression_stage の顔まわり要件
- 再実行条件
  - 関節潰れ failed
  - 食い込み failed
  - 左右差 failed

#### validation 呼び出し

- 各 stage は個別 validator を持つ
- 最終 validation は shape、look、rig、expression、weight を束ねた集約 report を返す
- failed がある場合は、どの stage を再実行すべきかを返さなければならない

#### dry-run / live 境界

- `dry_run` は、structured spec 解決、template 選択、予定 artifact、予定 validator を返す
- `live` は、Blender 実行コンテキストまたは公式 MCP 接続を必要とする処理を含む
- `live` が sidecar 単独で完結しない stage は、fallback で Blender 側実行経路へ切り替える

### 8.3.3 validation と auto-fix 契約

各 validator は、少なくとも次を返す。

- `status`
  - `pass`
  - `warning`
  - `failed`
- `stage`
- `check_name`
- `evidence`
- `suggested_fix`
- `retryable`

#### validator の粒度

- shape validator
  - silhouette
  - ratio
  - symmetry
- look validator
  - color
  - pattern placement
  - texture / UV integrity
- rig validator
  - hierarchy
  - naming
  - fit
- expression validator
  - key coverage
  - deformation correctness
  - neutral restore
- weight validator
  - joint deformation
  - clipping
  - left-right consistency

#### auto-fix ループ

- failed が `retryable=true` の場合、auto-fix ループ対象とする
- auto-fix は、validator の `stage` と `suggested_fix` を根拠に、対応 stage の再実行または spec 補正を行う
- 1 回の failed で複数 stage を同時再実行するのではなく、最小影響の stage から再実行する
- auto-fix の各反復では、少なくとも次を artifact に残す
  - 対象 stage
  - 失敗 validator
  - 適用した補正
  - 再実行結果

#### 停止条件

- 同一 validator が連続で閾値改善しない
- 再試行上限に達する
- 非 retryable failed が出る
- 上流 stage を壊す補正しか残らない

#### 最終失敗契約

- auto-fix で解消できなかった場合は、最終 report に次を残す
  - failed stage
  - failed validator
  - 最終 evidence
  - 試行回数
  - 失敗時 fallback 経路の有無

### 8.3.4 artifact と export 形式

作業ディレクトリは、少なくとも次の artifact を同一 run 単位で管理する。

- `prompt.txt`
- `character_spec.json` または `character_spec.yaml`
- `pipeline_spec.json` または `pipeline_spec.yaml`
- `stage_reports/`
- `validation/`
- `review/`
- `exports/`
- `run_manifest.json`

#### 必須 artifact

- `prompt.txt`
  - 元入力 prompt
- `character_spec`
  - 正規化後仕様
- `pipeline_spec`
  - 工程別実行仕様
- `stage_reports`
  - 工程ごとの結果
- `validation/final_validation_report.json`
  - 最終集約 report
- `validation/object_list.json`
  - object 一覧
- `review/`
  - front / side / back / perspective などの review 画像
- `exports/`
  - `.blend`
  - 必要に応じて `.glb`

#### `run_manifest.json`

`run_manifest.json` は、少なくとも次を持つ。

- `run_id`
- `source_prompt_hash`
- `character_type`
- `stages_executed`
- `fallbacks_used`
- `final_status`
- `exported_files`
- `artifact_paths`

#### traceability

- 各 artifact は `run_id` で相互参照できなければならない
- stage report には、対応する validator 結果と再試行履歴を紐付けなければならない
- export manifest から、どの prompt / spec / validation に対応する成果物か逆引きできなければならない

### 8.3.5 類型別テンプレートと初期ライブラリ境界

初期ライブラリは、少なくとも次の 4 系統で構成する。

- shape template
- rig template
- expression library
- pose test library

#### humanoid

- 標準二足人型の shape template
- 標準人型 rig template
- 基本表情セット
- 標準 pose test

#### chibi

- 短頭身特化 shape template
- chibi 比率の簡略 rig template
- 簡略化された基本表情セット
- chibi 体型向け pose test

#### creature

- 非人型部位を許容する shape template
- 追加肢、尾、翼などを含む拡張 rig template
- 類型別表情差分を持つ expression library
- creature 向け pose test

#### 共通化と差分

- 色味・材質・artifact 契約・validation 出力形式は共通化対象とする
- 部位構成、骨格構成、表情辞書、pose test は類型別差分対象とする
- 類型ごとの template は共通 schema に従うが、必須部位と必須骨の集合は異なってよい

### 8.3.6 ベースキャラクターデータ受け渡し契約

ベースキャラクターデータは、次の優先順位で受け取る。

- 第 1 優先
  - `base_character.blend`
- 第 2 優先
  - `base_character.fbx`
  - `base_character.glb`
- 補助ファイル
  - `notes.md`
  - `previews/front.png`
  - `previews/side.png`
  - `previews/back.png`
  - `previews/face_closeup.png`
  - `textures/`

#### `notes.md` 必須項目

`notes.md` は、少なくとも次を含む。

- main mesh object 名
- armature object 名
- face 用 object 名
- hair 用 object / collection 名
- 利用する texture directory
- UV 再利用可否
- face topology 再利用可否
- rig 再利用可否
- shape key 既存有無
- 改変許可範囲
- 改変禁止事項
- 目標キャラとの差分メモ

#### import 前 validation

ベースデータ import 前には、少なくとも次を確認する。

- main mesh object が特定できる
- armature object が特定できる、または未所持であることが明示されている
- UV が存在するか
- texture file path を解決できるか
- face topology を表情生成に流用できるか
- shape key が既にある場合、上書きか共存かを選べるか
- hair object / collection を本体と分離して扱えるか

#### 再利用範囲の記録

ベースデータ利用時の artifact には、少なくとも次を残す。

- `base_asset_manifest.json`
  - source file path
  - imported object list
  - imported armature list
  - imported material list
  - reusable_uv
  - reusable_face_topology
  - reusable_rig
  - reusable_shape_keys
  - reusable_hair_objects
- `adaptation_plan.json`
  - どの要件を流用するか
  - どの要件を再生成するか
  - どの object / armature / material を対象にするか

### 8.4 add-on integration

Blender add-on は、登録済み operator、Python API、batch 実行、context 準備の可否を確認できるものだけを自動化対象にする。

実行前に確認する項目:

- add-on が導入済みで、有効化可能である
- operator が registry に登録されている
- `poll` が成功する、または不足 context を準備できる
- modal / UI 専用 operator ではない
- 破壊的操作の場合は backup が作成されている
- 実行後の validation threshold が定義されている

`bpy.ops`、`bpy.context`、operator context override は context 依存が強いため、addon integration 実装の専用責務として扱う。
