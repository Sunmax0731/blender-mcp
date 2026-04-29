# 仕様

## 1. MVP 範囲

### 1.1 対象機能

- Blender との接続確認
- プリミティブ生成
- 基本変形
- オブジェクト一覧取得
- Blender UI からのメッセージ送信
- OpenAI 互換 API への最小問い合わせ

### 1.2 対象外

- 高度なメッシュ編集自動化
- マテリアルノード完全生成
- アニメーション/リギング自動生成

## 2. MCP ツール候補

### `blender_status`

- 目的: 接続状態を返す
- 入力: なし
- 出力: Blender 起動状態、アドオン接続状態、バージョン

### `blender_create_primitive`

- 目的: プリミティブ生成
- 入力: 種別、位置、回転、スケール
- 出力: 成否、生成オブジェクト名

### `blender_transform_object`

- 目的: 既存オブジェクト変形
- 入力: 対象名、位置/回転/スケール差分
- 出力: 成否、更新後状態

### `blender_list_objects`

- 目的: オブジェクト一覧取得
- 入力: フィルタ条件
- 出力: オブジェクト配列

### `blender_request_ai_suggestion`

- 目的: 選択中オブジェクトや要件に対する提案を取得
- 入力: プロンプト、選択情報、制約
- 出力: 提案テキストまたは構造化操作案

## 3. Blender UI 仕様

### 3.1 初期配置

- `View3D > Sidebar` に専用タブを追加

### 3.2 表示項目

- 接続状態
- リクエスト入力欄
- 実行履歴
- エラー表示
- 承認待ち操作一覧

### 3.3 操作

- `Connect`
- `Refresh Status`
- `Send Prompt`
- `Execute Approved Action`
- `Reject Action`

## 4. データ契約

### 4.1 構造化操作

```json
{
  "action": "create_primitive",
  "params": {
    "type": "CUBE",
    "location": [0, 0, 0],
    "scale": [1, 1, 1]
  },
  "requiresConfirmation": false
}
```

### 4.2 実行結果

```json
{
  "success": true,
  "requestId": "req-001",
  "message": "Cube created",
  "data": {
    "objectName": "Cube.001"
  }
}
```

## 5. 技術スタック候補

### 確定寄り

- Blender Add-on: Python
- MCP Server: Python
- テスト: pytest
- 品質管理: ruff, mypy

### 要検証

- MCP 実装: FastMCP または公式 Python SDK
- 通信: HTTP first, WebSocket later
- UI 補助: Blender 標準 UI で足りるか、将来的にカスタム描画が必要か

## 6. バージョン方針

- Python 3.11+ を基準とする
- Blender は LTS 系を優先し、具体版は要件確定 Issue で固定する

## 7. テスト対象

- コマンド検証
- Blender API 呼び出しラッパー
- 通信異常系
- 承認フロー
- AI 応答の構造化変換
