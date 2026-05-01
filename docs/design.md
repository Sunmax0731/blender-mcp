# 設計

## 1. 設計方針

- Blender 側の中核機能は公式 `blender_mcp` を採用する
- 本リポジトリは導入、自動化、Codex 統合、検証、配布を担う
- 外部サービス連携は、公式 MCP を置き換えず、補助 add-on と provider 層で追加する

## 2. アーキテクチャ

### 2.1 公式経路

```text
Codex App -> 公式 Blender MCP server -> 公式 Blender add-on -> Blender
```

### 2.2 補助 add-on 経路

```text
Blender UI -> Blender MCP supplemental add-on -> provider / plugin_bridge helper
```

### 2.3 installer 経路

```text
installer GUI
  -> PowerShell scripts
    -> official add-on / official server / Codex config / cleanup
    -> third-party plugins
    -> supplemental add-on
    -> optional precision profile
```

## 3. コンポーネント責務

### 3.1 公式 Blender MCP add-on

- Blender 内の bridge server を提供する
- 公式 tool 実行に必要な Blender 側処理を担う

### 3.2 公式 Blender MCP server

- MCP client からの tool 呼び出しを受ける
- 公式 add-on と通信する

### 3.3 installer

- 既存 PowerShell スクリプトを順番に実行する
- plugin manifest に従って第三者 plugin を導入する
- 補助 add-on を ZIP 化して install / enable する
- ログを保存し、失敗位置を明示する

### 3.4 Blender MCP supplemental add-on

- External Services 用 Preferences を提供する
- 3D View の `Blender MCP` パネルを提供する
- `Preferences 読み込み` と `サービス概要` を表示する

### 3.5 provider 層

- provider ごとに request / status / result import の責務を分離する
- 共通の HTTP helper と import helper を使う
- 生成系は `generate / poll / import` 契約へ寄せる

### 3.6 plugin bridge helper

- add-on の存在と有効化状態を点検する
- 必須 operator の可用性を確認する
- 最小 submit を行う

## 4. External Services 設計

### 4.1 共通設定

各 provider は少なくとも次を持つ。

- `enabled`
- `api_key`
- `endpoint`
- `mode`

### 4.2 共通 UI

3D View の `Blender MCP > 外部サービス` に次を持つ。

- `Preferences 読み込み`
- `サービス概要`
- `Service`
- `Prompt`
- `JSON`
- `Collection`
- `Submit / Poll / Import`

### 4.3 provider の位置づけ

- Meshy: provider 実装あり、plugin bridge 手動確認済み
- Tripo AI: provider 実装あり、plugin bridge 手動確認済み
- Hyper3D Rodin: provider 実装あり、plugin bridge 手動確認済み
- Stability API SPAR3D: provider 骨格あり、plugin bridge なし
- Poly Haven: provider 実装あり、UI は停止中

## 5. installer 設計

`v1.2.0` の標準 step は次です。

1. `official-addon`
2. `official-server`
3. `codex-config`
4. `enable-addon`
5. `remove-prompt-ui`
6. `third-party-plugins`
7. `supplemental-addon`
8. `precision-profile` 任意
9. `launch-blender` 任意

### 5.1 第三者 plugin 導入

- local payload 優先
- fallback URL を許容
- install method は `extension` と `addon_zip` を分ける

### 5.2 補助 add-on 導入

- runtime に含めた `blender_addon/blender_mcp` を一時 ZIP 化する
- Blender background で install と enable を行う
- user preferences を保存する

## 6. 安全設計

- 変更対象を GUI で事前表示する
- Codex 設定更新前にバックアップを作る
- 破壊的操作は通常導線では公開しない
- 外部サービス連携は experimental として扱い、実 API 成功保証を release 条件にしない

## 7. 既知制約

- RodinBridge は add-on 側の debug console を開く場合がある
- SPAR3D の plugin bridge は未実装
- Poly Haven は UI 停止中
- API キー未入手のため、`v1.2.0` は UI / installer / plugin bridge までを主な検証対象とする
