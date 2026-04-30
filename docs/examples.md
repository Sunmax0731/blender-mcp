# Blender MCP 実行例

## 1. カービィ風キャラクターモデル

Codex App から公式 Blender MCP を呼び出し、Blender 上に丸いキャラクターモデルを作成した例です。

prompt:

```text
Blenderでカービィ風の丸いキャラクターモデルを作成してください。
体はピンクの球体、手は左右に小さな丸い腕、足は赤い楕円形にしてください。
大きな青い目、白いハイライト、黒い瞳、赤い口、左右のピンクの頬も作成してください。

各パーツには分かりやすい名前を付け、マテリアルで色を設定してください。
ライトとカメラも配置し、正面から見やすい構図にしてください。
最後にシーン全体を確認し、作成したオブジェクト一覧と工夫した点を説明してください。
```

## 2. 公式 Example 1: Scene Analysis

参照元: [Blender MCP Server](https://www.blender.org/lab/mcp-server/)

目的は、現在開いている Blender scene を解析し、重い object、material、camera、light、改善候補を説明することです。

手順:

1. Blender で解析したい `.blend` を開く
2. 公式 `MCP` add-on が有効で server が running であることを確認する
3. Codex App で `blender-official` MCP server が有効であることを確認する
4. 次の prompt を Codex App に入力する

prompt:

```text
現在開いている Blender scene を解析し、object 構成、material、light、camera、品質上の懸念、改善案を日本語でまとめてください。
特に camera から見た表示サイズに対して polygon 数が多すぎる object があれば、理由と最適化案を説明してください。
```

確認観点:

- Codex が Blender scene の object / material / camera / light を参照して説明できる
- 変更を伴わず、分析結果として返る
- 改善案は実行ではなく提案として扱う

## 3. 公式 Example 2: Various Prompts

参照元: [Blender MCP Server](https://www.blender.org/lab/mcp-server/)

目的は、自然言語で複数種類の調査・整理・編集を依頼できることを確認することです。

prompt examples:

```text
現在開いている Blender ファイルで、分かりにくい data-block 名を調査し、より説明的な命名案を提案してください。適用は承認後にしてください。
```

```text
現在の scene で、指定した material を使っている object を一覧化してください。
```

```text
現在の Blender ファイルで最も面数が多い object を調べ、scene にリンクされていない object は除外してください。
```

```text
現在の Geometry Nodes setup の主な処理内容を説明し、必要なら frame と Text data-block でドキュメント化する案を提示してください。
```

確認観点:

- 変更前に対象と操作内容を確認できる
- material / mesh / Geometry Nodes など、対象を自然言語で指定できる
- 変更系の依頼では preview / confirm を挟む

## 4. precision workflow smoke

このリポジトリでは、公式 example の利用に加えて、precision profile の artifact を同一 directory に残す smoke を用意しています。

dry-run:

```powershell
uv run python scripts\run_precision_workflow_smoke.py --output-dir artifacts\precision-workflow-smoke
```

生成物:

- `scene_build_report.json`
- `validation_report.json`
- `review/review_manifest.json`
- `export_manifest.json`
- `prompt_samples.json`
- `smoke_summary.json`

Blender が起動済みで公式 MCP add-on が使える環境では、同じ流れを Blender 内 Python または公式 Blender MCP 経由で live 実行し、実際の screenshot / export artifact を確認します。
