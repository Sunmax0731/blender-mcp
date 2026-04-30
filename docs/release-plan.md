# 初回リリース計画

## 1. 目的
- 1 クリック導入アプリを含む Blender MCP の初回 Release を、再現可能なセットアップ手順と既知制約付きで公開する
- 初回利用者が「何を入れれば動くか」「どこまで動作確認済みか」を判断できる状態にする

## 2. リリース対象

v0.1.0 の詳細な scope と Go / No-Go 条件は [v0.1.0 release scope](release-scope-v0.1.0.md) で管理する。

### 2.0 初回 Release 版数

- このリポジトリの初回 GitHub Release 版数は `v0.1.0` とする
- これは本リポジトリの導入アプリと統合スクリプトの版数であり、公式 Blender MCP の版数とは分けて扱う
- 公式 Blender MCP の初期対応版は `v1.0.0` とする
- GitHub tag / Release 名称は `v0.1.0` を基準にする

### 2.1 配布物
- 1 クリック導入アプリ
  - `dist/one-click-installer/blender-mcp-installer.exe`
- 公式導入補助スクリプト
  - `scripts/install_official_blender_mcp.ps1`
  - `scripts/install_official_blender_mcp_server.ps1`
  - `scripts/register_official_blender_mcp_in_codex.ps1`
  - `scripts/enable_official_blender_mcp_addon.ps1`
- Python 実装
  - `src/blender_mcp_installer/`
- 利用手順と検証手順
  - `README.md`
  - `docs/validation-plan.md`
  - `docs/release-plan.md`

### 2.1.1 GitHub Release へ添付する配布物

添付 asset の詳細は [v0.1.0 release assets](release-assets-v0.1.0.md) を正とする。

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v0.1.0.json`

### 2.1.2 GitHub Release に添付しないもの

- `dist/official-blender-mcp/mcp-1.0.0.zip`
  - 公式 Blender MCP の配布物であり、このリポジトリの Release asset としては再配布しない
  - 導入時は公式配布元または取得済みキャッシュを使う
- Blender 本体
- Codex App 本体
- `.official-mcp-venv/`
- `artifacts/` 配下の検証ログ一式

### 2.2 初回リリースに含める機能
- 公式 add-on 配布物の取得
- Blender add-on 配置先への導入
- 公式 MCP server の専用仮想環境導入
- Codex 設定への `mcp_servers.blender-official` 登録
- 公式 `mcp` 有効化
- 導入ログの保存
- 導入後の確認項目表示
- 任意導入の v2 precision profile foundation
  - precision template / schema
  - sidecar MCP scaffold
  - static validation / visual QA dry-run
  - add-on registry inspection
  - Skill / AGENTS / subagent template

### 2.3 初回リリースに含めないもの
- Blender 本体の自動インストール
- Codex App 本体の自動インストール
- macOS / Linux 向け同時配布
- 公式 `blender_mcp` 自体の fork 改造
- 公開ネットワーク越しの常設運用
- v2 precision の全 tool 実装完了保証
- 任意 add-on operator 実行
- 公式 Blender MCP zip の Release asset としての再配布

## 3. リリース前チェック

### 3.1 自動確認
- `pytest` が成功する
- `uv run blender-mcp-installer --plan` が成功する
- 公式 MCP 経路の既存 round trip / live 確認が失敗していない

### 3.2 手動確認
- 1 クリック導入アプリが起動する
- 確認チェック後に導入開始できる
- ログ表示とログ保存先表示が機能する
- Blender の Add-ons 一覧で `MCP` が有効化される
- Codex App から公式 MCP tool が呼び出せる

### 3.3 live 接続確認
- Blender 起動状態で `get_screenshot_of_window_as_json` が成功する
- `jump_to_tab_by_name` によるワークスペース切替が成功する
- 接続結果を Issue コメントまたは Release ノートに残す

## 4. 既知制約
- 初回 Release 時点では `exe` 化手順や bundling 方法が配布工程に残る可能性がある
- Blender 本体と Codex App は事前導入を前提とする
- live 接続確認は Blender 起動状態に依存する
- Windows ローカル環境を第一対象としている
- 公式 Blender MCP 本体はこの Release で fork や再配布を行わず、対応版 `v1.0.0` を前提に導入する

## 5. リリース手順
1. `uv sync --python 3.11 --extra dev`
2. `uv run pytest`
3. `uv run blender-mcp-installer --plan`
4. Blender 実機で 1 クリック導入アプリの手動確認を行う
5. Codex App から公式 MCP tool の live 接続確認を行う
6. 配布物、README、`docs/` の既知制約、手順、証跡参照先を更新する
7. リリースノートまたは同等の公開情報を日本語で作成する

## 6. リリース判定
- P0/P1 の未解決不具合がない
- 自動確認と手動確認の証跡が揃っている
- 初回利用者向けのセットアップ手順が不足なく書かれている
- 既知制約が明文化されている
- 1 クリック導入アプリの配布方法が利用者に分かる形で整理されている
- Go / No-Go 条件は [v0.1.0 release scope](release-scope-v0.1.0.md) と一致している

## 7. リリース後の扱い
- 初回リリース後に見つかった制約や改善要望は GitHub Issue に分離して管理する
- 配布形態の改善と追加自動化は次フェーズ課題とする

## 8. Release milestone

v0.1.0 Release までの工程と Issue は [Release milestone plan](release-milestones.md) で管理する。

工程:

1. M1: Release scope freeze
2. M2: Packaging and installer validation
3. M3: Blender and Codex live validation
4. M4: Release publication
