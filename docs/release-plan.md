# 初回リリース計画

## 1. 目的
- Blender MCP の MVP を、再現可能なセットアップ手順と既知制約付きで公開する
- 初回利用者が「何を入れれば動くか」「どこまで動作確認済みか」を判断できる状態にする

## 2. リリース対象

### 2.1 配布物
- Blender add-on zip
  - `dist/blender_mcp_addon.zip`
- MCP サーバー実装
  - `src/blender_mcp_server/`
- Python 依存定義
  - `pyproject.toml`
  - `uv.lock`
- 利用手順と検証手順
  - `README.md`
  - `docs/validation-plan.md`
  - `docs/release-plan.md`

### 2.2 初回リリースに含める機能
- Blender add-on の有効化
- ローカル MCP サーバー起動
- `blender_status`
- `blender_create_primitive`
- `blender_list_objects`
- `blender_transform_object`
- `blender_delete_object` の承認付き実行
- Blender UI からの接続状態確認、プロンプト入力、履歴確認、承認操作
- OpenAI 互換 API への最小提案要求

### 2.3 初回リリースに含めないもの
- 任意 Python 実行
- 公開ネットワーク越しの遠隔操作
- 保存、エクスポートの自動実行
- 高度な複数オブジェクト一括操作
- AI 提案の品質保証

## 3. リリース前チェック

### 3.1 自動確認
- `pytest` が成功する
- `/mcp` 経由の round trip テストが成功する
- UI スモーク自動化が成功する
  - `controlled_launch`
  - `existing_process`

### 3.2 手動確認
- Blender の Add-ons 一覧から `Blender MCP` を有効化できる
- `View3D > Sidebar > Blender MCP` にパネルが表示される
- 日本語文言が文字化けしていない
- `Connect` `送信` `取得` `実行` `却下` の主要導線が操作できる
- reject 系操作時の表示と履歴が自然である

### 3.3 AI 連携確認
- OpenAI 互換 API 未設定時に適切なエラーを返す
- OpenAI 互換 stub または実環境で提案取得が成功する
- AI 提案文が履歴に表示される

## 4. 既知制約
- Blender UI スモークの `existing_process` は現在画面を撮影するだけで、画面内容の再現性は保証しない
- AI 提案品質はモデルとプロンプトに依存し、モデリング品質の保証は行わない
- 破壊的操作は限定 allowlist のみ対象とし、それ以外の高度な操作は後続フェーズで扱う
- Windows ローカル環境を第一対象としている

## 5. リリース手順
1. `uv sync --python 3.11 --extra dev`
2. `.venv\Scripts\python.exe -m pytest`
3. `powershell -ExecutionPolicy Bypass -File .\scripts\run_blender_ui_smoke.ps1`
4. Blender 実機で主要手動確認を行う
5. `dist/blender_mcp_addon.zip` を最終生成する
6. README と `docs/` の既知制約、手順、証跡参照先を更新する
7. リリースノートまたは同等の公開情報を日本語で作成する

## 6. リリース判定
- P0/P1 の未解決不具合がない
- 自動確認と手動確認の証跡が揃っている
- 初回利用者向けのセットアップ手順が不足なく書かれている
- 既知制約が明文化されている

## 7. リリース後の扱い
- 初回リリース後に見つかった制約や改善要望は GitHub Issue に分離して管理する
- AI 提案品質、承認フロー拡張、公開配布形態の改善は次フェーズ課題とする
