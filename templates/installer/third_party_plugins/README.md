# Third-Party Plugin Payloads

このディレクトリには、1 クリック導入アプリに同梱したい第三者 Blender plugin の ZIP を配置します。

- `third_party_plugins.json` の `payload_relpath` と一致するパスで置く
- ZIP がない場合、installer は `fallback_url` から取得を試みる
- 再配布条件が未確認の ZIP は同梱しない
