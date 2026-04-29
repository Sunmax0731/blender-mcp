# Blender Add-on Scaffold

`blender_addon/blender_mcp/` は `#4` の Blender アドオン最小スケルトンです。

含めているもの:

- `__init__.py` によるアドオン登録情報
- 多モジュール構成の登録/解除
- `Connection` `Session` `Approval` パネル
- 最小 Operator
- UI 状態を保持する `PropertyGroup`

まだ含めていないもの:

- 実際の MCP 通信
- 常時接続/再接続ロジック
- 承認付き削除実装
- チャット履歴の複数件保持
