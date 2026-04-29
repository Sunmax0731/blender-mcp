# 設計

## 1. 設計方針

- Blender 内ロジックは Blender アドオンに閉じる
- Codex との接点は MCP サーバーに集約する
- 外部 AI サービス接続はアダプタ層で抽象化する
- 危険操作は必ずポリシーと承認を通す

## 2. 想定アーキテクチャ

```text
Codex
  -> MCP Server (Python)
      -> Transport Layer (HTTP local / WebSocket candidate)
          -> Blender Add-on
              -> Blender Python API
      -> AI Provider Adapter
          -> OpenAI compatible API / other providers
```

## 3. コンポーネント

### 3.1 MCP Server

責務:

- Codex に公開するツール定義
- Blender 接続管理
- リクエスト検証
- 実行ジョブ管理
- AI プロバイダ呼び出し
- 監査ログ出力

候補実装:

- Python 3.11+
- FastMCP もしくは MCP Python SDK

### 3.2 Blender Add-on

責務:

- Blender UI 提供
- MCP サーバーとの通信
- Blender API 実行ラッパー
- 結果整形
- 例外捕捉

候補実装:

- Blender Python API
- `bpy.types.Panel`, `bpy.types.Operator`, `bpy.app.timers`

### 3.3 AI Provider Adapter

責務:

- API キー設定管理
- モデル呼び出し
- 応答正規化
- リトライ/タイムアウト

## 4. 通信方式比較

### 案A: ローカル HTTP

利点:

- 実装容易
- デバッグ容易
- ログや検証がしやすい

欠点:

- 疑似リアルタイムのためポーリング設計が必要

### 案B: WebSocket

利点:

- 双方向性が高い
- 状態同期に向く

欠点:

- Blender 側実装複雑度が上がる
- 安定化コストが高い

初期判断:

- MVP はローカル HTTP を採用
- 双方向イベントが不足した時点で WebSocket を再評価

## 5. 安全設計

- 実行コマンドは allowlist 型で管理する
- 引数スキーマを事前検証する
- 危険操作は `preview -> confirm -> execute` の 3 段階とする
- ローカルバインドのみを既定値にする

## 6. 監査/ログ

- MCP サーバー側に操作要求ログを記録
- Blender 側に実行結果ログを記録
- エラー時は例外種別、対象操作、主要引数を残す

## 7. 設計上の主なリスク

- Blender UI スレッドと通信処理の整合
- AI 応答の曖昧さによる不正操作
- バージョン差異による `bpy` API 挙動差
- 依存ライブラリが Blender 同梱 Python と衝突する可能性

## 8. リスク緩和

- 初期は操作種別を絞る
- 自然言語を直接実行せず構造化コマンドへ変換する
- Blender 側の通信依存を最小限に抑える
- 外部依存が重い処理は MCP サーバー側へ寄せる
