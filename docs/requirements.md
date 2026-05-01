# 要件定義

## 1. 背景

本リポジトリは、公式 `blender_mcp` を前提に、Windows 環境で Codex App / Codex CLI から Blender を扱える状態を再現しやすくすることを目的とする。

`v1.2.0` では、公式 Blender MCP 導入基盤に加えて、外部 3D サービス連携のための第三者 plugin 自動導入、補助 add-on 自動導入、共通 External Services UI を experimental 機能として公開する。

## 2. 目的

- 公式 Blender MCP を Windows 環境へ導入できるようにする
- Codex App から公式 MCP を使って Blender を操作できるようにする
- 第三者 plugin と補助 add-on を installer から導入できるようにする
- 外部 3D サービス連携の設定 UI と plugin bridge 状態確認を共通化する
- docs、検証計画、release 資産を `v1.2.0` 時点の実装に一致させる

## 3. 対象範囲

### 3.1 対象

- 公式 `blender_mcp` add-on / extension の導入支援
- 公式 `blender_mcp` server の利用前提整理
- Codex App からの公式 MCP 利用手順
- 既存開発版に残った不要な add-on 登録の cleanup
- 1 クリック導入アプリ
- Meshy / Tripo / Rodin plugin の自動導入
- 補助 Blender add-on の自動導入
- External Services 設定 UI と provider / plugin bridge 基盤
- 日本語ドキュメントと GitHub Issue 運用

### 3.2 非対象

- 公式 `blender_mcp` 自体の fork 前提改造
- 公式 add-on を全面的に置き換える独自 add-on 開発
- 公開ネットワーク前提の常設 server 構成
- 無制限の任意 Python 実行許可
- macOS / Linux 向け配布物の同時対応
- Blender 本体や Codex App 本体の自動インストール
- API キー未入手状態での外部サービス本番成功保証

## 4. 1クリック導入アプリ要件

### 4.1 成果物

- Windows ローカル環境で起動する GUI アプリを提供する
- 配布形態は `blender-mcp-installer.exe` とする
- Release asset として exe、sha256、release manifest を提供する

### 4.2 実行範囲

- 公式 add-on を取得し Blender へ導入する
- 公式 MCP server を専用 venv へ導入する
- Codex 設定へ `mcp_servers.blender-official` を追記する
- Blender 側で公式 `mcp` add-on を有効化する
- 旧補助 UI 登録を cleanup する
- 第三者 plugin を導入する
- 補助 Blender add-on を導入する
- 任意で precision profile を導入する

### 4.3 アプリが満たすべき性質

- 既存 PowerShell スクリプト資産を再利用する
- 利用者が失敗した step を識別できる
- 再実行時に致命的な競合を起こしにくい
- ローカル完結を前提とし、外部公開前提の常駐サービスを増やさない

## 5. 外部 3D サービス連携要件

### 5.1 共通 UI / 設定

- Blender Preferences に provider ごとの `enabled / api_key / endpoint / mode` を持つ
- Blender 側の UI は provider ごとに大きく分岐しない
- 3D View の `External Services` で状態表示、主操作、結果表示を共通化する

### 5.2 共通 adapter

- provider 単位で認証、submit、poll、import を分離する
- 生成系サービスは `generate / poll / import` の 3 段階契約に寄せる
- import 対象は初期段階では `glb / gltf` とする
- import した asset は専用 collection に集約する
- `plugin_bridge` mode では add-on 検出、有効化、必須 operator を事前点検できる

### 5.3 `v1.2.0` 時点の位置づけ

- Meshy / Tripo AI / Hyper3D Rodin / Stability API SPAR3D の UI と provider 骨格を含む
- `plugin_bridge` の手動確認済み対象は Meshy / Tripo / Rodin
- SPAR3D は `cloud_api` 前提で、plugin bridge は非対象
- Poly Haven は provider 実装のみ維持し、UI は停止中

## 6. 受け入れ条件

- 公式 Blender MCP の導入手順が再現可能である
- docs が `v1.2.0` 時点の実装に一致している
- 第三者 plugin と補助 add-on が installer から導入できる
- Blender 側で `Blender MCP` パネルと External Services 設定が確認できる
- `plugin_bridge` 概要で Meshy / Tripo / Rodin の状態を確認できる
- experimental 機能の範囲と既知制約が release notes に明記されている
