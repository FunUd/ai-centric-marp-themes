---
marp: true
theme: slate-minimal
paginate: true
header: "DESIGN PHILOSOPHY 2026"
footer: "© 2026 Slate Minimal"
---

<!-- _class: cover subtitle meta -->
<!-- _paginate: false -->

# Less, but better.
## ミニマリズムがもたらすデザインの真価と、次世代のUI設計。

Slate Minimal Theme | Design Division | 2026.05.16

---

<!-- _class: toc-focus -->

# AGENDA

1. なぜ今、ミニマリズムなのか
2. 基本原則とタイポグラフィ
3. プロダクト・ロードマップ
4. 最終的なデザインアウトプット

---

<!-- _class: profile -->

# 発表者紹介

<div class="profile-layout">
<div class="profile-content">

## 山田 太郎
### Taro Yamada / Lead Designer

デザインシステム「Slate Minimal」のリードデザイナー。
過剰な装飾を排し、本質的な情報伝達にフォーカスしたUI設計を専門としています。

- **経歴:** 10年以上のUI/UXデザイン経験
- **専門:** デザインシステム構築、ミニマリズム、タイポグラフィ
- **趣味:** モノクロ写真、建築デザインの探求

</div>
</div>

---

# タイポグラフィと階層化

テキストの大きさとウエイトだけで、情報の構造を明確に定義します。
色の装飾を一切排除し、**空白とコントラスト**のみで構成されます。

```css
/* Typography Scale */
h1 { font-size: 44px; font-weight: 400; font-family: 'Serif'; }
h2 { font-size: 34px; font-weight: 400; }
p  { font-size: 21px; color: var(--text-muted); }
```

> 良いデザインとは、可能な限りデザインしないことである。
> — ディーター・ラムス

---

<!-- _class: cols-2 -->

# デザインパラダイムの変遷

<div class="columns">
<div class="col">

### 過去のデザイントレンド
- リッチなテクスチャとシャドウ
- 複雑なグラデーションや色使い
- 情報を隙間なく詰め込むレイアウト
- **結果:** ユーザーの認知負荷が増大し、本来の目的から逸脱する

</div>
<div class="col">

### 現代のミニマリズム
- 本質のみを残したフラットデザイン
- タイポグラフィによる美しい階層化
- 意図的な余白（Whitespace）の活用
- **結果:** 直感的な操作と、ノイズのない洗練された情報伝達

</div>
</div>

---

<!-- _class: grid-sharp -->

# ミニマリズムの4原則

<div class="grid">
<div class="cell">

### 1. 削減 (Reduction)
不要な要素をすべて削ぎ落とす。装飾のための装飾は、情報伝達における罪である。

</div>
<div class="cell">

### 2. 整列 (Alignment)
見えないグリッドに従い、すべての要素を厳密に配置し、秩序を生み出す。

</div>
<div class="cell">

### 3. 強調 (Emphasis)
コントラストを利用し、最も重要なメッセージ一つだけを画面上で際立たせる。

</div>
<div class="cell">

### 4. 余白 (Whitespace)
何もない空間こそが、要素に意味と関係性を与え、息づかいを感じさせる。

</div>
</div>

---

<!-- _class: split-2 -->

# ビジュアルコンポーネント

<div class="columns">
<div class="col">

### アセットの活用
画像は元の色を保ったまま配置し、必要に応じて余白やサイズで視線誘導します。装飾効果に頼らず、情報そのものを際立たせます。

</div>
<div class="col">

<!-- ![shadow](https://dummyimage.com/800x600/e2e8f0/94a3b8.png&text=Architecture) -->
![assets](./assets/sample_image.jpg)

</div>
</div>

---

# スタイル一覧（表とバッジ）

| Component | Status | Description |
| :--- | :--- | :--- |
| Typography | <span class="badge ink">Core</span> | セリフ体とサンセリフ体の組み合わせ |
| Colors | <span class="badge green">Updated</span> | モノクロームを基調としたスレートカラー |
| Layouts | <span class="badge orange">Beta</span> | グリッド、カラム、タイムラインなど |
| Animations| <span class="badge red">Planning</span> | ホバー時の微細なインタラクション |

---

<!-- _class: steps -->

# 思考プロセス

1. **発散**
    アイデアを可能な限り多く出す。
2. **収束**
    本質的な価値だけを選び抜く。
3. **洗練**
    残った要素を磨き上げ、完成させる。

---

<!-- _class: cols-3 -->

# コールアウトの活用

<div class="columns">
<div class="col">

### 構造的課題
<div class="callout red">
情報の優先順位が不明確であり、ユーザーが迷う可能性が高い。
</div>

</div>
<div class="col">

### 視覚的課題
<div class="callout orange">
余白が不足しており、要素同士が干渉している。
</div>

</div>
<div class="col">

### 解決済み
<div class="callout green">
タイポグラフィの修正により、可読性が大きく向上した。
</div>

</div>
</div>

---

<!-- _class: timeline -->

# デザイン改修のタイムライン

1. **2026-07-01 コンポーネントの棚卸し**
   既存UIの要素を洗い出し、不要なものを整理
2. **2026-08-15 タイポグラフィの再定義**
   Serif と Sans-serif の組み合わせを策定
3. **2026-10-01 プロトタイプ作成**
   白黒のワイヤーフレームで構造を検証
4. **2026-11-15 最終リリース**
   新デザインシステム「Slate Minimal」を全面適用

---

<!-- _class: key-message -->

## DESIGN THE INVISIBLE.

見えない余白をデザインし、<br>ユーザーの思考をクリアにする。
