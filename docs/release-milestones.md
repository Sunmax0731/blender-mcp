# Release milestone plan

## 1. 目的

v0.1.0 Release までの工程を GitHub Milestone と Issue で追跡する。各工程は、前工程の完了証跡を確認してから次へ進む。

## 2. Milestone

### M1: Release scope freeze

- GitHub Milestone: [v0.1.0 M1: Release scope freeze](https://github.com/Sunmax0731/blender-mcp/milestone/1)
- 目的: Release 対象範囲、既知制約、利用者向け docs、release notes を確定する
- 完了条件: Release 判定条件、docs、release notes、asset 境界が確定している

Issues:

- [#73 Release までの工程を milestone と Issue に分解する](https://github.com/Sunmax0731/blender-mcp/issues/73)
- [#74 v0.1.0 release scope と Go / No-Go 条件を確定する](https://github.com/Sunmax0731/blender-mcp/issues/74)
- [#75 利用者向け setup / docs を release 前に最終確認する](https://github.com/Sunmax0731/blender-mcp/issues/75)
- [#76 v0.1.0 release notes 草案を確定する](https://github.com/Sunmax0731/blender-mcp/issues/76)
- [#77 Release asset / 再配布対象の境界を最終確認する](https://github.com/Sunmax0731/blender-mcp/issues/77)

### M2: Packaging and installer validation

- GitHub Milestone: [v0.1.0 M2: Packaging and installer validation](https://github.com/Sunmax0731/blender-mcp/milestone/2)
- 目的: installer exe、precision profile 任意導入、配布 asset、再現可能な build を検証する
- 完了条件: Release 添付 asset と installer 主要導線の検証証跡が揃っている

Issues:

- [#78 v0.1.0 installer exe を再ビルドし checksum を作成する](https://github.com/Sunmax0731/blender-mcp/issues/78)
- [#79 installer GUI / headless / plan の release smoke を実施する](https://github.com/Sunmax0731/blender-mcp/issues/79)
- [#80 precision profile 導入を一時 CodexHome で検証する](https://github.com/Sunmax0731/blender-mcp/issues/80)
- [#81 Release packaging manifest を作成する](https://github.com/Sunmax0731/blender-mcp/issues/81)

### M3: Blender and Codex live validation

- GitHub Milestone: [v0.1.0 M3: Blender and Codex live validation](https://github.com/Sunmax0731/blender-mcp/milestone/3)
- 目的: Blender 5.1、公式 MCP、Codex App、Blender UI、v2 precision の live / manual validation を揃える
- 完了条件: Blender / Codex App / Blender UI / v2 precision の検証証跡が Issue コメントに残っている

Issues:

- [#82 Blender 5.1 で公式 MCP add-on 導入 / 有効化を live 検証する](https://github.com/Sunmax0731/blender-mcp/issues/82)
- [#83 Codex App から公式 Blender MCP tool の live 接続を検証する](https://github.com/Sunmax0731/blender-mcp/issues/83)
- [#84 Blender UI Prompt の Plan / Confirm / Execute を手動 smoke する](https://github.com/Sunmax0731/blender-mcp/issues/84)
- [#85 v2 precision validation / visual QA / add-on inspection の release 証跡を採取する](https://github.com/Sunmax0731/blender-mcp/issues/85)

### M4: Release publication

- GitHub Milestone: [v0.1.0 M4: Release publication](https://github.com/Sunmax0731/blender-mcp/milestone/4)
- 目的: tag、GitHub Release、asset upload、公開後確認、follow-up backlog 作成を行う
- 完了条件: GitHub Release が公開され、asset download と公開後 smoke が確認されている

Issues:

- [#86 v0.1.0 GitHub Release draft を作成する](https://github.com/Sunmax0731/blender-mcp/issues/86)
- [#87 Release asset を upload して download 検証する](https://github.com/Sunmax0731/blender-mcp/issues/87)
- [#88 v0.1.0 Release を公開し公開後 smoke を実施する](https://github.com/Sunmax0731/blender-mcp/issues/88)
- [#89 Release 後 follow-up backlog を作成し milestone を閉じる](https://github.com/Sunmax0731/blender-mcp/issues/89)

## 3. 運用ルール

- milestone は M1 から順に完了させる
- 工程切替時は `docs/release-plan.md`、`docs/release-validation-v2.md`、この文書を見直す
- 判断が必要な場合は、該当 Issue に候補 3 案、判断基準、判断材料、推奨案をコメントする
- 実機確認が必要な Issue は、スクリーンショット、ログ、実行コマンド、失敗時の制約を Issue コメントへ残す
