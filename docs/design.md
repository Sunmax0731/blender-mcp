# 設計

## 1. 設計方針

- Blender 側の中核機能は公式 `blender_mcp` を採用する
- 本リポジトリは、公式配布物の導入、Codex 統合、自動化、検証を担当する
- 既存独自実装は段階的に縮退し、公式構成との差分を最小化する

## 2. アーキテクチャ

### 2.1 Codex App 経路

```text
Codex App
  -> 公式 MCP client
    -> 公式 Blender MCP server
      -> TCP socket bridge
        -> 公式 Blender add-on
          -> Blender
```

### 2.2 Blender 側の設定確認

Blender 内で利用者が確認する画面は公式 `MCP` add-on の Preferences とし、自然言語の制作指示は Codex App から行う。

## 3. コンポーネント責務

### 3.1 公式 Blender MCP add-on

- Blender 内で TCP bridge server を提供する
- 公式 tool 実行に必要な Blender 側処理を担う
- host / port / autostart などの基本設定を保持する

### 3.2 公式 Blender MCP server

- MCP クライアントから stdio / MCP tool 呼び出しを受ける
- 公式 add-on の bridge へ接続して Blender と通信する
- 公式 tool 群を提供する

### 3.3 本リポジトリの独自レイヤー

- 公式配布物の取得と導入自動化
- Codex App からの利用前提整理
- 旧開発版の不要な add-on 登録の cleanup
- 検証、更新、移行手順の自動化
- Blender MCP 作業品質を上げる配布用 Skill の管理

### 3.4 Blender 側の扱い

- 過去の開発版で残った `blender_mcp` add-on の不要な Preferences 登録は installer で cleanup する
- 公式 `mcp` add-on の通信設定や tool 実装は公式 add-on に集約する

### 3.5 1クリック導入アプリ層

- GUI から利用者の開始操作を受ける
- 各導入スクリプトを順番に実行する
- 実行ログを集約し、失敗時に停止位置を明示する
- 完了後に手動確認項目と次の操作を提示する

### 3.6 配布用 Skill 層

- `skills/` 配下に Codex Skill 形式で配置する
- `SKILL.md` は実行時に必要な短い指示に限定する
- 詳細な品質基準、チェックリスト、例は `references/` に分離する
- 利用者向けのコピー先と再起動手順は docs に記載する
- モデリング品質向け Skill と Blender アドオン開発向け Skill は用途が異なるため分離する

## 4. 1クリック導入アプリ設計

### 4.1 画面構成

- 初期画面
  - 前提条件の説明
  - 実行開始ボタン
- 実行中画面
  - 現在ステップ
  - 進捗表示
  - ログ表示
- 完了画面
  - 成功した処理一覧
  - 利用者が確認すべき項目
  - ログ保存先
- 失敗画面
  - 失敗ステップ名
  - エラーメッセージ
  - 再実行案内

### 4.2 内部処理フロー

1. Blender 実行ファイルと Codex 設定ファイルを解決する
2. 公式 add-on を導入する
3. 公式 MCP server を導入する
4. Codex 設定をバックアップして更新する
5. Blender 側 add-on 状態を公式寄りに切り替える
6. 旧開発版の不要な add-on 登録が残っていれば削除する
7. ログ保存と完了表示を行う

### 4.3 スクリプト統合方針

- 既存 PowerShell スクリプトをアプリ内部から呼び出す
- GUI 側は orchestration と表示に責務を限定する
- スクリプト間の入出力差異はラッパー層で吸収する
- 失敗時は後続処理へ進まず、その時点のログを保存する

### 4.4 ログ設計

- 標準出力と標準エラーをアプリ側で収集する
- 保存先は repo 外でも参照しやすいローカルディレクトリを選べるようにする
- 利用者向けメッセージと詳細ログを分ける
- Issue や検証証跡へ転記しやすい粒度でステップ名を揃える

### 4.5 安全設計

- 設定変更前に対象ファイルと変更内容を示す
- バックアップ作成後に書き換える
- 公式 add-on 有効化や設定追記は idempotent に近づける
- `preview -> confirm -> execute` を GUI フローにも反映する

## 5. 移行方針

### 5.1 短期

- docs を公式前提に切り替える
- 公式 add-on 導入スクリプトを整備する
- 既存独自スクリプトに「独自前提」であることを明記する

### 5.2 中期

- 独自 add-on / 独自 HTTP server を非推奨扱いにする
- Codex App から公式 MCP を使う実行経路を確認する
- 利用者向け導線は Codex App から公式 MCP を使う経路に一本化する

### 5.3 長期

- 公式更新追従の自動化
- 開発用の内部構成を利用者向け導線から分離する

## 6. リスク

- 公式更新で導入手順や内部構造が変わる
- Blender / add-on / MCP client の組み合わせ差で挙動差が出る
- 既存独自構成との混在期間に誤接続が起こる
- GUI 層と既存スクリプトの責務分離が曖昧だと保守が難しくなる

## 7. 対応方針

- 公式版と独自版を明確に区別する
- 導入スクリプトは公式配布物のバージョンを明示する
- docs と Issue に、どの構成を対象にしているか必ず記録する
- GUI は薄く保ち、導入ロジックは既存スクリプト群へ寄せる
- Codex App 経路を正とする
- 配布用 Skill は、品質チェックと作業手順を提供し、公式 MCP の tool 実装は持たない

## 8. v2 精密モデリング設計

### 9.1 推奨アーキテクチャ

```text
Codex App / Codex CLI
  -> blender-precision-mcp sidecar
    -> 公式 Blender MCP server
      -> 公式 Blender add-on
        -> Blender scene / approved add-ons
```

sidecar は、公式 Blender MCP の tool を置き換えるのではなく、制作計画、検証、視覚レビュー、承認済み add-on 実行を高水準 tool としてまとめる。

### 9.2 sidecar の責務

- `blender_precision_config.yaml` を読み込む
- profile / tool pack / policy を解決する
- `tools/list` で公開 tool を切り替える
- `model_spec.yaml` と JSON Schema を検証する
- 破壊的操作前に backup と preview を要求する
- 公式 Blender MCP への低水準操作を集約する
- validation report と review screenshot を保存する

### 9.2.1 sidecar と Blender 実行の境界

- sidecar は dry-run、static validation、artifact 設計、scene snapshot を使った検証のオーケストレーションを担当する
- sidecar 自身が `bpy` を保持しているとは限らないため、`create_or_update_scene_from_spec(dry_run=false)` や `export_scene(dry_run=false)` は Blender 実行コンテキストが必要である
- 利用者向け docs では、`blender_unavailable` を sidecar 不具合ではなく実行コンテキスト境界として説明する
- live 成果物は `model_spec`、validation report、object list、review 画像、export manifest を同一 artifact directory にまとめる

### 9.2.2 全自動キャラクター生成の責務分離

#### sidecar の責務

- prompt を `character_spec` と `pipeline_spec` へ正規化する
- 類型別 template / library を選択する
- stage 実行順序を決定する
- validator 実行結果を集約する
- auto-fix の再試行制御を行う
- artifact manifest と traceability 情報を管理する

#### 公式 Blender MCP の責務

- Blender scene の状態取得
- object、material、camera、light などの低水準操作
- scene snapshot と screenshot の取得
- sidecar が必要とする live inspection の中継

#### Blender 実行コンテキストの責務

- `bpy` を必要とする live shape 生成
- UV / texture 適用を含む material 実処理
- armature、shape key、weight の適用
- pose test に必要な Blender 内処理
- `.blend` や `.glb` の最終 export

#### fallback 設計

- sidecar 単独で `bpy` 必須処理を完結できない stage は、Blender background 実行または公式 MCP 経由へ切り替える
- fallback は stage 単位で発動し、run 全体を巻き戻さない
- fallback 発動時も、artifact と report に使用経路を残す

### 9.2.3 5要件パイプラインのコンポーネント分割

全自動トラックの実装単位は、少なくとも次のコンポーネントに分ける。

- prompt normalizer
- shape generator
- look generator
- rig builder
- expression builder
- weight builder
- validation coordinator
- auto-fix controller
- artifact manager

#### 再実行単位

- `shape generator`
  - silhouette、比率、部位構成の失敗時に再実行
- `look generator`
  - 色味、模様、texture / UV の失敗時に再実行
- `rig builder`
  - 命名、親子関係、寸法フィットの失敗時に再実行
- `expression builder`
  - 表情 coverage、neutral 復帰、左右破綻の失敗時に再実行
- `weight builder`
  - pose test、食い込み、左右差の失敗時に再実行

#### 依存関係

- `look generator` は `shape generator` の出力に依存する
- `rig builder` は `shape generator` の出力に依存する
- `expression builder` は `shape generator` と `rig builder` に依存する
- `weight builder` は `shape generator`、`rig builder`、必要に応じて `expression builder` に依存する
- `validation coordinator` は全 stage の出力を参照する
- `auto-fix controller` は validator の失敗結果を参照して最小影響の stage を再実行する

### 9.2.4 validator と auto-fix の実行モデル

- validator は stage 実行直後の局所検証と、最終集約検証の 2 段階で実行する
- `validation coordinator` は、局所 failed を stage 単位に集約し、再実行候補を `auto-fix controller` へ渡す
- `auto-fix controller` は、同時多発 failed でも最上流原因を優先して処理する
- 同一 run では、再試行履歴と改善量を比較し、改善が頭打ちなら停止する
- 非 retryable failed は、その時点で設計上の fallback か最終失敗へ遷移させる

### 9.2.5 類型別テンプレートとライブラリ管理

- 類型別テンプレートは `humanoid`、`chibi`、`creature` の 3 系統で管理する
- テンプレートとライブラリは、少なくとも次を別管理する
  - shape template
  - rig template
  - expression library
  - pose test library
  - material preset
- 共通 schema を保ちながら、類型ごとの差分はテンプレートデータで吸収する
- テンプレート更新時は、どの類型のどの stage に影響するかを artifact と release notes で追跡できるようにする

### 9.2.6 artifact と traceability の保存設計

- `artifact manager` は run ごとのルートディレクトリを払い出し、全 stage の成果物をそこへ集約する
- stage report、validator 結果、retry 履歴、review 画像、export は `run_id` で相互参照可能にする
- debug 用の中間成果物と、利用者向け最終成果物は同じ run 配下で層分けして保存する
- 後追い調査では、prompt、template 選択、validator failed、fallback 発動、最終 export を 1 本の trace として復元できなければならない

### 9.3 Codex 設定の責務分離

Codex の STDIO MCP 設定では、`command` / `args` は server 起動用とする。公開 tool の増減は、sidecar server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で扱う。

このため、設計上は「`args` で tool を注入する」のではなく、「`args` で profile / config / tool pack を渡し、sidecar server が公開 tool を選ぶ」と表現する。

### 9.4 add-on 実行設計

add-on operator 実行は、通常のモデリング tool から分離する。

- `addon_registry` に承認済み add-on と operator を登録する
- `inspect_addons` で導入済み add-on と operator capability を確認する
- `prepare_operator_context` で mode、selection、active object、area override を準備する
- `check_operator_poll` で実行可能性を確認する
- `run_approved_addon_operator` は registry と policy を通過したものだけを実行する

modal operator、UI 専用 operator、未承認 operator は通常導線では実行しない。

### 9.5 配布設計

利用者へ配布するものは、installer で選択導入できる形に寄せる。

- precision profile 用 Codex MCP 設定例
- `AGENTS.md` テンプレート
- `SKILL.md` と参照資料
- subagent template
- `model_spec.yaml` / `blender_precision_config.yaml` テンプレート
- validation / visual QA script
