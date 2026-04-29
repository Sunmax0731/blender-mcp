# 仕様

## 1. MVP 範囲

### 1.1 対象機能

- Blender との接続確認
- プリミティブ生成
- 基本変形
- オブジェクト一覧取得
- Blender UI からのメッセージ送信
- OpenAI 互換 API への最小問い合わせ
- 許可操作の制御
- 承認待ち操作の表示

### 1.2 対象外

- 高度なメッシュ編集自動化
- マテリアルノード完全生成
- アニメーション/リギング自動生成
- 任意 Python コード実行
- 破壊的操作の自動実行
- 公開ネットワーク越し制御

## 1.3 MVP 操作 allowlist

MVP では、Blender 側で受け付ける操作を明示的な allowlist で管理する。

### 自動実行を許可する操作

- `blender_status`
  - 接続状態確認のみ
- `blender_list_objects`
  - オブジェクト名、型、選択状態などの読み取り
- `blender_create_primitive`
  - `CUBE` `UV_SPHERE` `ICO_SPHERE` `CYLINDER` `CONE` `PLANE`
  - 位置、回転、スケールは安全な数値範囲に制限する
- `blender_transform_object`
  - 単一オブジェクトへの位置、回転、スケール変更
  - 対象オブジェクト名の明示指定を必須とする
  - 極端な値は拒否できるようにする

### 承認後のみ実行を許可する操作

- オブジェクト削除
- モディファイア適用
- 既存データ上書き
- 複数オブジェクトを一括で変更する操作
- 将来追加される破壊的操作

### MVP で禁止する操作

- 任意 Python スクリプト実行
- アドオン外部からの自由形式 `bpy` 呼び出し
- ファイル保存、エクスポート、上書き保存の自動実行
- ジオメトリノード、マテリアルノード、リグ、アニメーションの自動生成
- 公開ネットワーク経由の操作受付

## 2. MCP ツール候補

### `blender_status`

- 目的: 接続状態を返す
- 入力: なし
- 出力: Blender 起動状態、アドオン接続状態、バージョン
- 実行区分: 自動実行可

### `blender_create_primitive`

- 目的: プリミティブ生成
- 入力: 種別、位置、回転、スケール
- 出力: 成否、生成オブジェクト名
- 実行区分: 自動実行可
- 制約:
  - 種別は allowlist 内に限定する
  - 生成数は 1 回の要求で 1 個までを基本とする
  - 座標とスケールは安全な範囲で検証する

### `blender_transform_object`

- 目的: 既存オブジェクト変形
- 入力: 対象名、位置/回転/スケール差分
- 出力: 成否、更新後状態
- 実行区分: 自動実行可
- 制約:
  - 対象は単一オブジェクトに限定する
  - 対象名未指定は受け付けない
  - 変形量が閾値を超える場合は失敗または承認対象へ送る

### `blender_list_objects`

- 目的: オブジェクト一覧取得
- 入力: フィルタ条件
- 出力: オブジェクト配列
- 実行区分: 自動実行可

### `blender_request_ai_suggestion`

- 目的: 選択中オブジェクトや要件に対する提案を取得
- 入力: プロンプト、選択情報、制約
- 出力: 提案テキストまたは構造化操作案
- 実行区分: 提案生成のみ
- 制約:
  - AI 応答は即時実行しない
  - 必ず構造化候補または説明文として返す

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

### 3.4 表示上の区別

- 自動実行可能な操作
- 承認待ちの操作
- 拒否された操作
- allowlist 外で失敗した操作

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

### 4.3 操作区分

```json
{
  "action": "transform_object",
  "executionMode": "auto",
  "requiresConfirmation": false,
  "policyReason": null
}
```

`executionMode` は少なくとも以下を持つ。

- `auto`
- `confirm_required`
- `rejected`

### 4.4 共通メタデータ

すべての主要レスポンスは、少なくとも以下のメタデータを持つ。

```json
{
  "requestId": "req-001",
  "timestamp": "2026-04-29T18:00:00+09:00",
  "success": true
}
```

### 4.5 `blender_status` レスポンス

```json
{
  "requestId": "req-001",
  "timestamp": "2026-04-29T18:00:00+09:00",
  "success": true,
  "data": {
    "blenderRunning": true,
    "addonLoaded": true,
    "addonVersion": "0.1.0",
    "blenderVersion": "4.2.0",
    "transportStatus": "connected"
  }
}
```

`transportStatus` の候補:

- `connected`
- `disconnected`
- `timeout`

### 4.6 `blender_create_primitive` リクエスト

```json
{
  "action": "create_primitive",
  "params": {
    "type": "CUBE",
    "name": "Block_A",
    "location": [0, 0, 0],
    "rotationEuler": [0, 0, 0],
    "scale": [1, 1, 1]
  },
  "requiresConfirmation": false
}
```

制約:

- `type` は allowlist 内のみ
- `name` は任意
- `location` `rotationEuler` `scale` は 3 要素数値配列

### 4.7 `blender_create_primitive` レスポンス

```json
{
  "requestId": "req-002",
  "timestamp": "2026-04-29T18:00:03+09:00",
  "success": true,
  "data": {
    "objectName": "Block_A",
    "objectType": "MESH",
    "createdPrimitiveType": "CUBE"
  }
}
```

### 4.8 `blender_transform_object` リクエスト

```json
{
  "action": "transform_object",
  "params": {
    "targetObjectName": "Block_A",
    "location": [1, 0, 0],
    "rotationEuler": [0, 0, 0.785398],
    "scale": [1, 2, 1],
    "mode": "absolute"
  },
  "requiresConfirmation": false
}
```

`mode` の候補:

- `absolute`
- `delta`

### 4.9 `blender_transform_object` レスポンス

```json
{
  "requestId": "req-003",
  "timestamp": "2026-04-29T18:00:05+09:00",
  "success": true,
  "data": {
    "objectName": "Block_A",
    "location": [1, 0, 0],
    "rotationEuler": [0, 0, 0.785398],
    "scale": [1, 2, 1]
  }
}
```

### 4.10 `blender_list_objects` リクエスト

```json
{
  "action": "list_objects",
  "params": {
    "namePrefix": "Block_",
    "selectedOnly": false,
    "typeFilter": ["MESH", "LIGHT"]
  }
}
```

### 4.11 `blender_list_objects` レスポンス

```json
{
  "requestId": "req-004",
  "timestamp": "2026-04-29T18:00:07+09:00",
  "success": true,
  "data": {
    "objects": [
      {
        "name": "Block_A",
        "type": "MESH",
        "selected": true,
        "visible": true
      }
    ]
  }
}
```

### 4.12 `blender_request_ai_suggestion` リクエスト

```json
{
  "action": "request_ai_suggestion",
  "params": {
    "prompt": "選択中オブジェクトを少し横長にしたい",
    "selectedObjects": [
      {
        "name": "Block_A",
        "type": "MESH"
      }
    ],
    "sceneSummary": {
      "objectCount": 4,
      "selectedObjectCount": 1
    },
    "constraints": {
      "allowActions": ["transform_object"],
      "disallowActions": ["delete_object"]
    }
  }
}
```

### 4.13 `blender_request_ai_suggestion` レスポンス

```json
{
  "requestId": "req-005",
  "timestamp": "2026-04-29T18:00:10+09:00",
  "success": true,
  "data": {
    "suggestions": [
      {
        "summary": "X 方向のスケールを広げる",
        "proposedAction": {
          "action": "transform_object",
          "params": {
            "targetObjectName": "Block_A",
            "scale": [1.5, 1, 1],
            "mode": "delta"
          },
          "requiresConfirmation": false
        }
      }
    ]
  }
}
```

### 4.14 共通エラー応答

```json
{
  "requestId": "req-006",
  "timestamp": "2026-04-29T18:00:12+09:00",
  "success": false,
  "error": {
    "code": "BLENDER_NOT_RUNNING",
    "message": "Blender が起動していません。",
    "retryable": true,
    "details": {
      "transportStatus": "disconnected"
    }
  }
}
```

`code` の初期候補:

- `BLENDER_NOT_RUNNING`
- `ADDON_NOT_READY`
- `ACTION_NOT_ALLOWED`
- `CONFIRMATION_REQUIRED`
- `INVALID_ARGUMENT`
- `AI_PROVIDER_ERROR`
- `INTERNAL_ERROR`

### 4.15 シーン要約スキーマ

```json
{
  "sceneSummary": {
    "sceneName": "Scene",
    "objectCount": 12,
    "selectedObjectCount": 2,
    "objectTypes": {
      "MESH": 8,
      "LIGHT": 2,
      "CAMERA": 1
    }
  }
}
```

### 4.16 選択オブジェクトスキーマ

```json
{
  "selectedObject": {
    "name": "Block_A",
    "type": "MESH",
    "location": [0, 0, 0],
    "rotationEuler": [0, 0, 0],
    "scale": [1, 1, 1]
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
