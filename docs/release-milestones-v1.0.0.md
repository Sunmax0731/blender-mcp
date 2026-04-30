# v1.0.0 release milestone plan

## 1. 目的

`v1.0.0` 正式 Release までの工程を GitHub Milestone と Issue で追跡する。

各工程は、前工程の完了証跡を Issue コメントと docs に残してから次へ進む。

## 2. Milestone

### M1: Formal release scope and user docs

- GitHub Milestone: [v1.0.0 M1: Formal release scope and user docs](https://github.com/Sunmax0731/blender-mcp/milestone/5)
- 目的: 正式 Release の scope、Go / No-Go、利用者向け導入・利用 docs を確定する
- 完了条件: Release scope と利用者向け docs が整備され、README から到達できる

Issues:

- [#94 Release 後 docs: v0.1.0 の導入手順を利用者向けに再確認する](https://github.com/Sunmax0731/blender-mcp/issues/94)
- [#95 v1.0.0 正式 Release scope と Go / No-Go 条件を確定する](https://github.com/Sunmax0731/blender-mcp/issues/95)
- [#96 v1.0.0 利用者向け導入手順書・利用方法・機能説明を整備する](https://github.com/Sunmax0731/blender-mcp/issues/96)

### M2: Installer and config safety

- GitHub Milestone: [v1.0.0 M2: Installer and config safety](https://github.com/Sunmax0731/blender-mcp/milestone/6)
- 目的: installer UX、Finish 導線、既存 Codex `config.toml` の安全な扱いを整える
- 完了条件: installer の安全性、plan、log、復旧手順が docs と実装で一致している

Issues:

- [#93 precision profile installer: 既存 Codex config.toml への安全なマージ方針を決める](https://github.com/Sunmax0731/blender-mcp/issues/93)
- [#97 v1.0.0 installer の正式 Release 向け UX と安全性を確認する](https://github.com/Sunmax0731/blender-mcp/issues/97)

### M3: Blender/Codex validation and precision boundary

- GitHub Milestone: [v1.0.0 M3: Blender/Codex validation and precision boundary](https://github.com/Sunmax0731/blender-mcp/milestone/7)
- 目的: Blender / Codex live validation と v2 precision の正式範囲を確認する
- 完了条件: 正式機能の live validation が完了し、precision は optional experimental の境界が明記されている

Issues:

- [#90 v2 precision: Blender live scene validation を実測化する](https://github.com/Sunmax0731/blender-mcp/issues/90)
- [#91 v2 precision: visual QA の live screenshot 比較を自動化する](https://github.com/Sunmax0731/blender-mcp/issues/91)
- [#92 v2 precision: approved add-on operator の live integration を検証する](https://github.com/Sunmax0731/blender-mcp/issues/92)

### M4: Release packaging and publication

- GitHub Milestone: [v1.0.0 M4: Release packaging and publication](https://github.com/Sunmax0731/blender-mcp/milestone/8)
- 目的: tag、Release、asset upload、公開後 smoke、follow-up backlog を完了する
- 完了条件: `v1.0.0` Release が公開され、asset download と公開後 smoke が確認されている

Issues:

- [#98 v1.0.0 Release asset / manifest / checksum を作成して検証する](https://github.com/Sunmax0731/blender-mcp/issues/98)
- [#99 v1.0.0 GitHub Release を公開し公開後 smoke を実施する](https://github.com/Sunmax0731/blender-mcp/issues/99)

## 3. 運用ルール

- milestone は M1 から順に完了させる
- 判断が必要な Issue には候補 3 案、判断基準、判断材料、推奨案を残す
- 実機確認が必要な Issue は、スクリーンショット、ログ、実行コマンド、失敗時の制約を Issue コメントへ残す
- v2 precision は v1.0.0 では optional experimental とし、正式 Release の blocker にはしない
- 工程切替時は `docs/release-scope-v1.0.0.md`、`docs/release-milestones-v1.0.0.md`、`docs/release-plan.md` を見直す
