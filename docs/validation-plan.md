# 検証計画

## 1. 目的

- 公式 Blender MCP を前提とした導入手順が再現できることを確認する
- 1 クリック導入アプリから主要導入ステップを一括実行できることを確認する
- Codex App / Codex CLI 連携の前提条件が崩れていないことを確認する
- docs と実装方針が一致していることを確認する

## 2. 検証レベル

### 2.1 静的確認

- docs の日本語表記確認
- 公式参照 URL の妥当性確認
- スクリプト引数、既定値、導入先の確認
- 1 クリック導入アプリの実行ステップと docs の一致確認

### 2.2 導入確認

- 公式 `mcp-1.0.0.zip` が取得できる
- ローカル展開できる
- Blender extension 管理経路へ導入できる
- Blender の `Get Extensions` で `MCP` が認識される
- 公式 `mcp` が有効化される
- 旧 `blender_mcp` add-on の Preferences 登録が残っている場合に削除される
- 公式 MCP server を専用仮想環境へ導入できる
- `blender-mcp --help` が実行できる
- Codex 設定へ `mcp_servers.blender-official` を追記できる
- `blender-mcp-installer --plan` で実行予定ステップを確認できる
- 1 クリック導入アプリから各 PowerShell ステップを順番に呼び出せる

### 2.3 live 接続確認

- Blender 起動後に Codex App から公式 MCP tool を呼び出せる
- `get_screenshot_of_window_as_json` が成功する
- `jump_to_tab_by_name` によりワークスペース切替が成功する

### 2.4 運用確認

- 公式構成を前提にした docs が読み替え不要で使える
- 導入・更新手順が PowerShell / コマンドプロンプトで実行できる
- 利用者向け導線が公式 `mcp` 前提として読める
- `start_official_blender_mcp.ps1` から Blender 実行パスを解決できる
- Codex App から Blender ワークスペース切替や状態取得が実行できる
- 1 クリック導入アプリのログから失敗箇所を追跡できる

### 2.5 Blender 側 cleanup 確認

- 利用者向け導線が Codex App と公式 MCP に一本化されている
- 公式 `MCP` add-on は有効なまま残る
- cleanup step は旧 `blender_mcp` 登録がない環境でも成功する
- cleanup step のログから削除対象と公式 add-on 状態を確認できる

## 3. 証跡

- スクリプト実行ログ
- `blender-mcp-installer` 実行ログ
- 展開済みファイル一覧
- Blender add-on 配置結果
- 公式 `mcp` 有効化ログ
- 公式 MCP server 専用仮想環境の作成結果
- Codex 設定更新結果
- Codex App からの接続結果
- 旧開発版 add-on 登録 cleanup 結果
- Issue コメント

## 4. 完了条件

- 公式 add-on 導入スクリプトが通る
- 1 クリック導入アプリ経由でも主要導入が追跡できる
- docs が公式前提に更新済みである
- Issue 上で移行方針と結果が追跡できる

## 5. v2 精密モデリング検証

### 5.1 静的検証

- `blender_precision_config.yaml` が schema と一致する
- `model_spec.yaml` が schema と一致する
- `validation_report` が schema と一致する
- Codex MCP 設定例で `command` / `args` が server 起動設定として記載されている
- tool の実行時引数が `tools/call` の `arguments` として説明されている
- `enabled_tools` / `disabled_tools` と sidecar の `tools/list` の責務が docs と一致している

### 5.2 sidecar MCP 検証

- profile ごとに公開 tool が変わる
- tool pack ごとに公開 tool が変わる
- policy block された tool が公開または実行されない
- `startup_timeout_sec` / `tool_timeout_sec` の設定例が導入手順と矛盾しない
- structured result に成功、失敗、警告、証跡パスが含まれる
- `bpy` 非接続時に `blender_unavailable` が期待どおり返り、docs の切り分け手順と一致する

### 5.3 Blender scene 検証

- `model_spec` の寸法、パーツ、材質、命名に沿ってシーンを検証できる
- mesh cleanup、non-manifold、loose geometry、quad ratio などの結果を report に残せる
- viewport screenshot を指定ビューで保存できる
- 検証失敗時に修正候補が report に残る
- Blender Python 外では visual QA manifest を dry-run で作成できる
- 導入直後の正常系として、`blender-official` 接続確認、`blender_precision` dry-run、Blender 側 live 実行の順が docs と一致する
- live 実行時に validation report、object list、review 画像を同じ artifact directory に残せる

### 5.4 add-on integration 検証

- 導入済み add-on 一覧を取得できる
- approved add-on registry にない operator は実行できない
- operator の `poll` と context 条件を確認できる
- modal / UI 専用 operator は structured failure として扱う
- 破壊的 operator の前に backup が作成される

### 5.5 配布検証

- installer から precision profile / Skill / template の導入有無を選べる
- 導入後に Codex App 再起動が必要な場合、その案内が表示される
- `AGENTS.md` / `SKILL.md` / subagent template の配置先が docs と一致している

## 6. 全自動キャラクタートラックの pre-test 検証

M5 テスト工程へ入る前に、少なくとも次の実装完了と確認が必要である。

### 6.1 base asset 経路

- `BaseAvatar.vrm` から `.blend` を生成できる
- `base_character_package` と artifact の両方に `.blend` を保存できる
- `.blend` から `base_asset_manifest.json` と `adaptation_plan.json` を生成できる
- pipeline が base asset あり / なしで分岐できる

### 6.2 image reference 経路

- `front / side / back / face_closeup / expression_*` を受理できる
- `image_reference_manifest.json` を出力できる
- prompt / image conflict を traceability に残せる

### 6.3 hair preset 経路

- 初期 hair preset を `character_spec` から選択できる
- hair object を live build に反映できる
- hair object を validation と artifact に反映できる

### 6.4 retry / traceability 経路

- retryable failed を stage 単位で再試行できる
- retry 履歴と改善量を artifact に残せる
- 非 retryable failed と停止条件を report に残せる

## 7. 全自動キャラクタートラックの M5 テスト項目

pre-test 実装が揃った後、M5 では次をテスト対象にする。

### 7.0 現在の実行順

2026-04-30 時点では、M5 を次の順で進める。

1. [#159](https://github.com/Sunmax0731/blender-mcp/issues/159) dry-run 入力経路 regression
2. [#160](https://github.com/Sunmax0731/blender-mcp/issues/160) live Blender build と strict validation regression
3. [#161](https://github.com/Sunmax0731/blender-mcp/issues/161) hair preset と retry traceability regression

### 7.1 dry-run regression

- prompt だけで `character_spec` / `pipeline_spec` / validation artifact が出る
- base asset 入力あり / なしで run manifest が整合する

### 7.2 live Blender regression

- live scene build が通る
- rig / shape key / weight artifact が出る
- strict validation と review artifact が残る

### 7.3 base asset reuse regression

- `BaseAvatar.blend` を入力にした pipeline 分岐が通る
- reuse / regenerate 判定が期待どおり artifact に残る

### 7.4 image reference regression

- 画像入力が色、髪シルエット、顔特徴へ反映される
- conflict ルールが artifact に残る

### 7.5 hair preset regression

- hair preset ごとに live build が通る
- hair object の naming / material / validation が崩れない

### 7.6 retry traceability regression

- retryable failed の再実行が行われる
- retry traceability が run manifest と stage report に残る
