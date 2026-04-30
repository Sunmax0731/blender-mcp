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
