# blender-mcp v1.2.0

`v1.2.0` は、公式 Blender MCP 導入基盤に加えて、外部 3D サービス連携の補助 UI と plugin 自動導入を experimental 機能として公開する Release です。

## 主な変更

- installer から Meshy / Tripo / Rodin plugin を自動導入できるようにした
- installer から `Blender MCP` 補助 add-on を自動導入できるようにした
- Blender Preferences に External Services 共通設定を追加した
- 3D View の `Blender MCP` パネルに External Services UI を追加した
- Meshy / Tripo / Rodin の `plugin_bridge` 状態確認を追加した
- SPAR3D の provider 骨格と共通 UI を追加した
- 利用者向け導入手順、利用方法、設計書、要件定義書、検証計画を `v1.2.0` に合わせて更新した

## この Release で確認済みのこと

2026年5月1日時点で次を確認済みです。

- installer が第三者 plugin を導入できる
- installer が補助 add-on を導入できる
- Blender Preferences に External Services が表示される
- 3D View の `Blender MCP` タブに External Services が表示される
- `サービス概要` に次が出る
  - Meshy: `plugin_bridge ready (Meshy official plugin)`
  - Tripo AI: `plugin_bridge ready (Tripo 3D)`
  - Hyper3D Rodin: `plugin_bridge ready (RodinBridge)`
  - Stability API SPAR3D: `plugin bridge 定義なし`

## experimental として扱う範囲

- Meshy / Tripo AI / Hyper3D Rodin / Stability API SPAR3D の External Services 連携
- API キー前提の `cloud_api`
- `generate / poll / import` の実サービス成功

理由:

- API キー未入手のため、今回の Release 条件は UI、installer、plugin bridge、手動導線確認までとしている

## 既知制約

- SPAR3D の plugin bridge は未実装
- Poly Haven は provider 実装のみ保持し、UI からは非表示
- RodinBridge は add-on 側の debug console を開く場合がある

## GitHub Release に添付するもの

- `blender-mcp-installer.exe`
- `blender-mcp-installer.exe.sha256`
- `release-manifest-v1.2.0.json`
