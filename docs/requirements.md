# 要件定義

## 1. 背景

本プロジェクトは、Blender 公式の `blender_mcp` を前提に、Codex App から Blender を扱えるようにすることを目的とする。

従来の独自 add-on / 独自 MCP server 構成は、更新追従と実運用の安定性に課題がある。今後は公式配布物と公式責務分離を優先し、このリポジトリは導入・統合・自動化・検証を担う。

## 2. 目的

- 公式 Blender MCP を Windows 環境へ導入できるようにする
- Codex App から公式 MCP server を経由して Blender を操作できるようにする
- Blender への自然言語指示は Codex App から行い、公式 MCP 導線に一本化する
- 公式更新に追従しやすい運用基盤を整える
- Release 成果物として、1 クリックで導入を進められる Windows 向けアプリを提供する

## 3. 対象範囲

### 3.1 対象

- 公式 `blender_mcp` add-on / extension の導入支援
- 公式 `blender_mcp` server の利用前提整理
- Codex App からの公式 MCP 利用手順
- 既存開発版に残った不要な add-on 登録の cleanup
- 導入・更新・検証スクリプト
- 1 クリック導入アプリ
- 日本語ドキュメントと Issue 運用

### 3.2 非対象

- 公式 `blender_mcp` 自体の fork 前提改造
- 公式 add-on を全面的に置き換える独自 add-on 開発
- Blender 側から Codex を直接呼び出す独自操作導線
- 公開ネットワーク前提の常設 server 構成
- 無制限の任意 Python 実行許可
- macOS / Linux 向け配布物の同時対応
- Blender 本体や Codex App 本体の自動インストール

## 4. 1クリック導入アプリ要件

### 4.1 成果物

- Windows ローカル環境で起動する GUI アプリを提供する
- 利用者は原則 1 回の起動操作で導入フローを開始できる
- 配布形態は Python 製 GUI ラッパーを `exe` 化したものを初期方針とする

### 4.2 アプリが実行する範囲

- 公式 add-on 配布物を取得し、Blender add-on 配置先へ導入する
- 公式 MCP server を専用仮想環境へ導入する
- `%USERPROFILE%\.codex\config.toml` 相当の Codex 設定へ `mcp_servers.blender-official` を追記する
- Blender 側で公式 `mcp` add-on を有効化する
- 導入後の確認項目とログ保存先を利用者へ提示する

### 4.3 アプリが満たすべき性質

- 既存 PowerShell スクリプト資産を可能な限り内部利用する
- 失敗したステップを利用者が識別できる
- 再実行時に致命的な競合を起こしにくい
- ローカル完結を前提とし、外部公開前提の常駐サービスを増やさない

### 4.4 前提条件

- 利用者の PC に Blender 5.1 系が導入済みである
- 利用者の PC に Codex App が導入済みである
- ネットワーク接続により公式配布物を取得できる
- ローカル設定変更を許可できる Windows 環境である

## 5. MVP

### 5.1 MVP で満たすこと

- 公式 `mcp-1.0.0.zip` をローカルへ導入できる
- Blender 5.1 系で公式 add-on を有効化できる
- Codex App から公式 MCP を使う前提が docs で明確化されている
- 利用者向け導線が Codex App と公式 MCP に一本化されている
- 公式構成への移行計画が Issue / docs に残っている
- 1 クリック導入アプリの要件、対象、非対象、配布方針が明確化されている

### 5.2 MVP 以降

- Codex App からの実運用コマンド群の拡張
- 公式更新時の差分検知と更新自動化
- 1 クリック導入アプリの GUI 実装と `exe` 配布
- 導入後の live 接続確認自動化

## 6. Blender 側の扱い

Blender 側では公式 `MCP` add-on の Preferences を確認対象とする。

### 6.1 対象

- 公式 `MCP` add-on の Preferences による host / port / autostart 確認
- 旧開発版 add-on の不要な Preferences 登録 cleanup
- Codex App から公式 MCP を使う利用手順の明確化

### 6.2 非対象

- Blender から Codex CLI を直接呼び出すこと
- 確認なしの任意 Python 実行
- ユーザー確認を省略したシーン破壊操作

## 7. 受け入れ条件

- 公式配布物の導入手順が再現可能である
- 公式構成を前提にした docs が日本語で整備されている
- 既存独自構成との差分と縮退方針が明確である
- GitHub Issue 上で判断経緯が追跡できる
- 1 クリック導入アプリの成果物定義と適用範囲が追跡できる
- 利用者向け導線を Codex App と公式 MCP に一本化する判断が追跡できる

## 8. v2 精密モデリング要件

v2 では、公式 Blender MCP を土台に、より高品質なモデル制作、検証、視覚レビュー、Blender add-on 活用を行うための sidecar MCP server と配布用テンプレートを追加対象とする。

### 8.1 対象

- Codex から呼び出す高水準 tool 群を提供する `blender-precision-mcp` sidecar / proxy
- profile / config / tool pack に応じた MCP tool 公開制御
- `model_spec.yaml` による制作意図、寸法、構成要素、材質、検証条件の明文化
- `validation_report` によるシーン検証、メッシュ検証、材質検証、視覚レビュー証跡
- `addon_registry` による承認済み Blender add-on、operator、property map、検証基準の管理
- Codex 向け `AGENTS.md` / `SKILL.md` / subagent template の配布
- 利用者が導入できる precision profile / Skill / template の installer 連携

### 8.2 非対象

- Codex MCP 設定の `args` で tool を直接注入する設計
- 未承認 add-on operator の実行
- UI 操作や modal operator 前提の自動化
- 確認なしの破壊的シーン編集
- 任意 Python / `bpy` 実行を利用者向け通常導線で許可すること

### 8.3 安全要件

- `command` / `args` は MCP server 起動のために使い、公開 tool は server の `tools/list` と Codex 側の `enabled_tools` / `disabled_tools` で制御する
- `args` で渡すのは profile、config、tool pack などの server 起動設定に限定する
- 破壊的操作はバックアップ作成と `preview -> confirm -> execute` を必須にする
- add-on 利用は承認済み registry、operator poll、context 準備、dry-run 可能性を確認してから実行する
- `bpy.ops` / `bpy.context` / operator context override は add-on integration の設計領域として分離する
- sidecar 単独では `bpy` 非依存の dry-run と static validation を正とし、`bpy` 必須の live 処理は Blender 側実行経路を用意する
- precision profile 導入後の利用者は、`blender-official` 接続確認、`blender_precision` dry-run、live 実行の順に到達できなければならない
- live 実行の完了条件には validation report、object list、review 画像などの artifact 採取を含める

## 9. 全自動キャラクターモデル生成トラック

prompt のみを入力として、次の 5 要件をすべて自動で満たすキャラクターモデル制作基盤を新トラックとして扱う。

1. キャラクターの形状をメッシュで再現する
2. キャラクターの色味や模様をテクスチャ、マテリアルで再現する
3. キャラクターのボーンを自動設定する
4. キャラクターの表情変化をシェイプキーで再現する
5. キャラクターの姿勢変化を正しく設定できるウェイトを再現する

### 9.1 要件定義の初期方針

- 単発の自然文 prompt を直接 Blender 操作へ流さず、いったん structured spec へ変換する
- 形状、見た目、rig、shape key、weight を別工程として扱い、それぞれに validator を持つ
- 完全自動の完了条件には、見た目だけでなく rig・表情・変形品質の検証証跡を含める
- 失敗時は 1 回で諦めず、差分修正ループと artifact 比較を前提にする

### 9.2 prompt 駆動オーケストレーション要件

#### 9.2.1 入力契約

- 利用者入力は自然文 prompt のみを基本とする
- 自然文 prompt から、少なくとも次を含む structured spec を内部生成できなければならない
  - キャラクター類型
  - 体型と部位比率
  - 色味、模様、材質
  - 骨格類型
  - 必須表情セット
  - 変形検証用 pose 条件
- 初期対象類型は `humanoid`、`chibi`、`creature` の 3 類型とする
- 見た目再現の初期要件には、マテリアル、UV、画像テクスチャを含める

#### 9.2.2 内部工程

- 自動生成パイプラインは、少なくとも次の工程に分割されなければならない
  1. prompt 理解
  2. structured spec 生成
  3. 形状生成
  4. テクスチャ・マテリアル生成
  5. ボーン設定
  6. シェイプキー生成
  7. ウェイト設定
  8. validation
  9. 差分修正
- 各工程は独立した artifact と validation 結果を持ち、失敗箇所を特定できなければならない
- 各工程の出力は後続工程の入力契約として再利用できなければならない

#### 9.2.3 自動検証

- validation は、最低でも次の 4 系統を持たなければならない
  - 形状 validation
  - 見た目 validation
  - rig / shape key validation
  - pose / weight validation
- validation は pass / warning / failed の区別を持ち、failed の場合は修正候補を返せなければならない
- 完全自動の完了条件は、5 要件すべてが validation 上で success と判定されることとする

#### 9.2.4 差分修正ループ

- 失敗時は単に停止するのではなく、structured spec または生成結果の差分修正ループを実行できなければならない
- 修正ループでは、どの工程のどの validator が失敗したかを根拠として扱わなければならない
- 修正回数、停止条件、最終失敗時の報告形式を定義しなければならない

#### 9.2.5 artifact 契約

- 少なくとも次の artifact を同一作業ディレクトリに保存できなければならない
  - 元 prompt
  - structured spec
  - 中間 validation report
  - 最終 validation report
  - object list
  - review 画像
  - export manifest
- artifact は工程ごとの差分比較と再実行判断に使える形式で保存しなければならない

#### 9.2.6 失敗時フォールバック

- sidecar 単独で完結しない live 処理は、Blender 側実行経路へ切り替えられなければならない
- `bpy` 非接続、scene snapshot 不足、texture 生成失敗、rig 適用失敗、weight 破綻など、代表的失敗種別ごとにフォールバック方針を持たなければならない
- フォールバック後も、どの経路を使って最終成果物を得たかを artifact と report に残さなければならない

### 9.3 形状メッシュ自動生成要件

- shape 生成は、少なくとも正面、側面、背面のシルエット整合を評価対象に含めなければならない
- structured spec には、頭身、肩幅、胴体長、腕脚長、手足サイズ、髪ボリューム、衣装外形を含めなければならない
- 初期対象類型 `humanoid`、`chibi`、`creature` ごとに、最低限の部位セットと寸法制約を定義しなければならない
- 形状品質の受け入れ条件は、少なくとも次を含まなければならない
  - 部位欠損がない
  - 左右対称性が維持される
  - 指定した頭身・部位比率の許容差内に収まる
  - major silhouette が prompt 意図から逸脱していない
- 自動修正ループでは、部位比率、位置、シルエット崩れを差分対象として扱わなければならない

### 9.4 テクスチャ・マテリアル自動再現要件

- 見た目再現は、部位ごとに base color、roughness、metallic、normal、alpha、emission を定義できなければならない
- 初期要件として UV 展開と画像テクスチャ適用を含めなければならない
- 模様再現は、少なくとも単色、左右対称模様、画像テクスチャ由来模様を扱えなければならない
- material 設定と texture asset は別 artifact として追跡できなければならない
- 見た目品質の受け入れ条件は、少なくとも次を含まなければならない
  - 指定色と主要配色関係が維持される
  - 主要模様の位置と境界が大きく崩れない
  - 部位ごとの質感差が区別できる
  - UV や texture 由来の破綻が許容閾値内である

### 9.5 ボーン自動設定要件

- rig は、初期対象類型ごとに骨格テンプレートを切り替えられなければならない
- humanoid / chibi では、最低でも root、hips、spine、neck、head、arm、leg、hand、finger の基本骨格を持たなければならない
- creature では、追加肢や尾などの拡張骨格を扱える設計でなければならない
- 骨格品質の受け入れ条件は、少なくとも次を含まなければならない
  - 命名規則が一貫している
  - 左右対応骨が判別できる
  - 主要関節の親子関係が正しい
  - 寸法フィット後も不自然な骨長や回転軸にならない
- rig 工程は後続の shape key、weight、pose test で再利用できる一貫した骨格契約を持たなければならない

### 9.6 シェイプキーによる表情自動生成要件

- 初期要件として、少なくとも笑顔、怒り、驚き、まばたき、口形状の基本表情セットを扱わなければならない
- 表情生成は、自然文 prompt から表情辞書または表情 spec へ正規化して扱わなければならない
- 顔 topology は、shape key の変形に必要な最小 edge flow を満たしていなければならない
- 表情品質の受け入れ条件は、少なくとも次を含まなければならない
  - 左右破綻がない
  - まぶた、口角、頬、眉の主要変形が意図どおり動く
  - 基本表情間で相互干渉が許容範囲内である
  - neutral 顔へ戻したときに破綻が残らない

### 9.7 ウェイトペイントと姿勢変化自動設定要件

- 初期姿勢は T ポーズまたは検証しやすい基準ポーズを持たなければならない
- ウェイト設定は、肩、股関節、肘、膝、手首、足首、指、顔周辺の主要変形点を対象に含めなければならない
- pose test は、最低でも腕上げ、肘曲げ、膝曲げ、開脚、首回転、指曲げを検証対象に含めなければならない
- 変形品質の受け入れ条件は、少なくとも次を含まなければならない
  - 関節周辺の潰れや食い込みが閾値内である
  - 主要 pose でメッシュ破綻がない
  - 左右で同系統の pose 結果が大きくずれない
  - shape key と骨変形の併用時にも重大破綻が出ない
- pose test の失敗は validator により工程別に特定でき、再ウェイトまたは骨格補正の根拠として使えなければならない
