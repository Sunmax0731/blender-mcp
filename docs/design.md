# 設計

## 1. 設計方針

- Blender 側の中核機能は公式 `blender_mcp` を採用する
- 本リポジトリは、公式配布物の導入、Codex 統合、補助 UI、自動化を担当する
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

### 2.2 Blender UI 補助経路

```text
Blender UI
  -> 補助ブリッジ
    -> Codex CLI
      -> 提案 / 実行計画
        -> 公式 Blender MCP または Blender 補助処理
```

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
- Blender UI から Codex CLI を使う補助導線
- 検証、更新、移行手順の自動化

## 4. 移行方針

### 4.1 短期

- docs を公式前提に切り替える
- 公式 add-on 導入スクリプトを整備する
- 既存独自スクリプトに「独自前提」であることを明記する

### 4.2 中期

- 独自 add-on / 独自 HTTP server を非推奨扱いにする
- Codex App から公式 MCP を使う実行経路を確認する
- Blender UI から Codex CLI を使う補助経路を、公式 add-on 非依存で設計する

### 4.3 長期

- 公式更新追従の自動化
- 旧独自構成の削除または隔離

## 5. リスク

- 公式更新で導入手順や内部構造が変わる
- Blender / add-on / MCP client の組み合わせ差で挙動差が出る
- 既存独自構成との混在期間に誤接続が起こる

## 6. 対応方針

- 公式版と独自版を明確に区別する
- 導入スクリプトは公式配布物のバージョンを明示する
- docs と Issue に、どの構成を対象にしているか必ず記録する
