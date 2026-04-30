# Blender MCP 実行例

このページでは、Codex App から公式 Blender MCP を呼び出し、Blender 上に結果を作成した実例を記録します。

## 1. カービィ風キャラクターモデル

- 関連 Issue: [#52](https://github.com/Sunmax0731/blender-mcp/issues/52)
- 掲載 Issue: [#53](https://github.com/Sunmax0731/blender-mcp/issues/53)
- 実行日: 2026-04-30
- 経路: `Codex App -> 公式 MCP server -> 公式 Blender add-on -> Blender`

### プロンプト

```text
Blenderでカービィを作ってください。
色もマテリアルで設定してくれると嬉しいです。
```

### 結果

Blender 内に `Issue52_Kirby_Style_Model` コレクションを作成し、丸いピンクのキャラクターモデルを配置しました。

主な構成は次のとおりです。

- 体、左右の手、左右の足、頬、目、口を個別のメッシュオブジェクトとして作成
- 体と手に淡いピンク、足に赤系、頬にローズピンク、目に黒・青・白のマテリアルを設定
- 専用カメラ `Kirby_Model_Camera` とライトを追加
- 初期 Cube / Camera / Light を整理し、確認しやすいシーンに調整

![カービィ風キャラクターモデルの Blender MCP 実行結果](assets/examples/issue-52-kirby-style-model.png)

### 検証

- `get_objects_summary` で `Issue52_Kirby_Style_Model` に 24 オブジェクトがあることを確認
- Blender の OpenGL レンダリングで確認画像を生成
- 生成した `.blend` と確認画像を `artifacts/` に一時保存し、掲載用画像を `docs/assets/examples/` へ移動

### 補足

この例は、公式 Blender MCP による Python 実行で Blender シーンを直接構成したものです。危険操作を伴う自動化ではなく、ローカル Blender 上のシーン生成とマテリアル設定の確認を目的としています。

## 2. 公式 Example 1: Scene Analysis

- 参照元: [Blender MCP Server](https://www.blender.org/lab/mcp-server/)
- 対象: 既存 `.blend` の解析
- 推奨 demo file: 公式ページで紹介されている Classroom demo file
- 経路: `Codex App -> 公式 MCP server -> 公式 Blender add-on -> Blender`

### 目的

Blender MCP を使って、開いているシーンの重いオブジェクトや最適化候補を調べます。公式ページでは、単純なポリゴン数だけでなく、カメラから見た画面上の大きさに対してポリゴン数が多いオブジェクトを探す例が紹介されています。

### 実行手順

1. Blender で解析したい `.blend` を開く
2. 公式 `mcp` add-on が有効で、Blender 側の bridge が起動していることを確認する
3. Codex App で `blender-official` MCP server が使えることを確認する
4. Codex へ、カメラ視点で小さく見えるがポリゴン数が多い外れ値を列挙するよう依頼する
5. 結果を見て、テクスチャ化、Subdivision level 調整、不要 mesh の削減などの候補を判断する

### 依頼例

```text
現在開いている Blender シーンを解析し、カメラから見た表示サイズに対してポリゴン数が多すぎるオブジェクトを一覧化してください。最適化候補と理由も説明してください。
```

### 確認観点

- 対象が現在開いている `.blend` になっている
- カメラが設定されている
- viewport 用 modifier だけでなく、最終レンダーや modifier 設定の差も必要に応じて確認する
- 結果は自動修正ではなく、まず最適化候補として扱う

## 3. 公式 Example 2: Various Prompts

- 参照元: [Blender MCP Server](https://www.blender.org/lab/mcp-server/)
- 対象: 既存 `.blend` に対する複数種類の問い合わせや編集
- 推奨 demo file: 公式ページで紹介されている Scattering Pebbles demo file
- 経路: `Codex App -> 公式 MCP server -> 公式 Blender add-on -> Blender`

### 目的

Blender MCP を使い、自然言語でシーン内の data-block、material、poly-count、Geometry Nodes などを調査または整理します。公式ページでは、data-block 名の修正、より分かりやすい命名案、material 利用元の問い合わせ、poly-count の調査、Geometry Nodes の説明追加などが例示されています。

### 実行手順

1. Blender で対象の demo file または手元の `.blend` を開く
2. 公式 `mcp` add-on と Codex App の `blender-official` 接続を確認する
3. 変更を伴う依頼では、まず「提案のみ」または「承認後に適用」と明記する
4. Codex へ data-block、material、mesh、Geometry Nodes などの対象を自然言語で指定する
5. 結果を Blender 側で確認し、必要なら保存前に Undo または別名保存する

### 依頼例

```text
現在開いている Blender ファイルで、分かりにくい data-block 名を調査し、より説明的な命名案を提案してください。適用は承認後にしてください。
```

```text
現在のシーンで、指定した material を使っている object を一覧化してください。
```

```text
現在の Blender ファイルで最も面数が多い object を調べ、シーンにリンクされていない object は除外してください。
```

```text
現在の Geometry Nodes setup の主な処理内容を説明し、必要なら frame と Text data-block でドキュメント化する案を提示してください。
```

### 確認観点

- 変更系の依頼では、実行前に提案内容を確認する
- data-block 名の変更は参照関係や既存命名規則への影響を確認する
- material や object の問い合わせ結果は Outliner / Properties でも確認する
- Geometry Nodes への frame 追加や Text data-block 作成は、既存 node tree を壊さない範囲で行う

### 補足

公式ページの Example 2 は、利用する LLM と対象 demo file により結果が変わる前提です。このリポジトリでは、公式例をそのまま実行するだけでなく、`preview -> confirm -> execute` の運用に合わせて、変更前確認を入れる形で利用します。
