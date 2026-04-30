# 配布用 Skill

このリポジトリでは、Blender MCP を使った作業品質を上げるための Codex Skill を `skills/` 配下に配置します。

## 1. 利用できる Skill

### blender-quality-modeling

- パス: `skills/blender-quality-modeling/`
- 目的: Blender MCP または Blender Python 経由で、より品質の高いモデル、マテリアル、ライト、カメラ、検証証跡を作る
- 主な対象:
  - Blender モデル作成
  - 既存シーンの見た目改善
  - マテリアルやライトの追加
  - ドキュメント掲載用のレンダー確認

### blender-addon-development

- パス: `skills/blender-addon-development/`
- 目的: Blender アドオン / extension の設計、実装、検証、配布手順を整える
- 主な対象:
  - Blender Python add-on の作成
  - Operator / Panel / Property / Preferences の設計
  - `register()` / `unregister()` の確認
  - add-on の手動 UI スモークと配布前チェック

### precise-blender-modeling template

- パス: `templates/precision/skills/precise-blender-modeling/`
- 目的: v2 precision profile、`model_spec.yaml`、validation、visual QA、approved add-on wrapper を前提にした精密モデリング手順を配布する
- 主な対象:
  - 仕様駆動の Blender モデル作成
  - validation report と review image を含む成果物作成
  - approved add-on registry を使った mesh cleanup / retopology
  - v2 sidecar MCP server の tool pack 利用

## 2. インストール

利用者の Codex 環境で Skill として使う場合は、必要な Skill ディレクトリを Codex の skill ディレクトリへコピーします。

PowerShell 例:

```powershell
Copy-Item -Recurse -Force .\skills\blender-quality-modeling "$env:USERPROFILE\.codex\skills\blender-quality-modeling"
Copy-Item -Recurse -Force .\skills\blender-addon-development "$env:USERPROFILE\.codex\skills\blender-addon-development"
Copy-Item -Recurse -Force .\templates\precision\skills\precise-blender-modeling "$env:USERPROFILE\.codex\skills\precise-blender-modeling"
```

Codex App が起動中の場合は、コピー後に Codex App を再起動してください。

v2 precision profile を project template として使う場合は、次も利用者の作業プロジェクトへコピーします。

```powershell
Copy-Item -Force .\templates\precision\agents\AGENTS.md <project>\AGENTS.md
Copy-Item -Recurse -Force .\templates\precision\subagents <project>\.codex\subagents
```

`<project>` は、Blender 制作用の作業プロジェクトに置き換えてください。

## 3. 使い方

Blender モデル作成や品質改善を依頼するときに、次のような依頼で利用できます。

```text
Blender MCP で高品質なロボットのモデルを作成してください。マテリアル、ライト、カメラ、確認画像も設定してください。
```

Skill は、モデルを部品に分ける、マテリアル名を付ける、ライトとカメラを置く、レンダー確認する、といった品質確認観点を Codex に与えます。

Blender アドオン開発を依頼するとき:

```text
Blender 5.1 向けに、選択オブジェクトの情報を表示する Sidebar add-on を設計して実装してください。
```

Skill は、manifest、Operator、Panel、Property、登録解除、検証手順といったアドオン開発の確認観点を Codex に与えます。

## 4. 運用方針

- 配布用 Skill は `skills/<skill-name>/SKILL.md` を入口にする
- 詳細な品質基準は `references/` に分ける
- 利用者向け README には概要とインストール先だけを載せる
- Skill を更新した場合は、`agents/openai.yaml` と validation も確認する
- v2 precision template は repo 運用用の `AGENTS.md` と混ぜず、`templates/precision/` を配布元にする
