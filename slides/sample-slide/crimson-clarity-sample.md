---
marp: true
theme: crimson-clarity
paginate: true
header: "Crimson Clarity Demo"
footer: "© 2026 Your Company"
---

<!-- _class: cover subtitle meta -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Crimson Clarity

## ビジネスプレゼンテーション テーマ

プレゼンター名 | 部署名 | 2026年4月

---

<!-- _class: toc -->

# 目次

1. 箇条書きスライド
2. テーブル表示
3. 2カラムレイアウト
4. 3カラムレイアウト
5. カラム内の配置指定
6. 4象限グリッド
7. ステップ表示
8. タイムライン
9. チェックリスト
10. コールアウトとバッジ
11. キーメッセージ
12. コードブロック

---

<!-- _class: toc-focus -->

# アジェンダ (少項目向け)

1. 現状の課題と背景
2. 提案するソリューション
3. 導入のロードマップ
4. 期待される効果

---

<!-- _class: with-header -->

# 箇条書きスライド

## グループ名付き

- **プロジェクト管理**
  - タスクの優先順位付け
  - マイルストーンの設定
  - リソースの最適配分
- **品質管理**
  - コードレビューの実施
  - テスト自動化の推進
  - パフォーマンス監視

---

# テーブル表示

| 機能 | Basic | Pro | Enterprise |
|------|-------|-----|------------|
| ユーザー数 | 10名まで | 100名まで | 無制限 |
| ストレージ | 10GB | 100GB | 1TB |
| サポート | メール | 電話+メール | 24/7専任 |
| API連携 | ✕ | ○ | ○ |
| カスタマイズ | ✕ | △ | ○ |

---

<!-- _class: cols-2 -->

# 2カラムレイアウト

<div class="columns">
<div class="col">

### 現状の課題

- 手動プロセスが多い
- データが分散している
- レポート作成に時間がかかる
- 属人化が進んでいる

</div>
<div class="col">

### 提案するソリューション

- ワークフロー自動化
- データ統合プラットフォーム
- リアルタイムダッシュボード
- ナレッジベースの構築

</div>
</div>

---

<!-- _class: cols-3 -->

# 3カラムレイアウト

<div class="columns">
<div class="col">

### Phase 1

**基盤構築**

要件定義とインフラ設計を実施

</div>
<div class="col">

### Phase 2

**開発・テスト**

アジャイル開発とQAテストを反復

</div>
<div class="col">

### Phase 3

**展開・運用**

本番デプロイと監視体制の確立

</div>
</div>

---

<!-- _class: split-2 -->

# 分割レイアウト（背景・枠線なし）

<div class="columns">
<div>

| 比較項目 | 従来型 | 新型 |
|----------|--------|------|
| 処理速度 | 中 | 高 |
| コスト | 高 | 低 |
| 拡張性 | 低 | 高 |

</div>
<div>

### シンプルな2分割

背景の赤色カードや枠線を適用せずに、純粋に画面を2分割したい場合は `split-2` や `split-3` クラスを使用します。

左側に表、右側にテキストといったレイアウトを組む際に、背景が目立ちすぎずクリーンな見た目を保つことができます。

</div>
</div>

---

<!-- _class: cols-2 -->

# カラム内の配置指定 (cols)

<div class="columns">
<div class="col v-center text-center">

### 中央揃え
`v-center text-center`

垂直・水平ともに中央に配置されます。カード形式のレイアウトで視覚的に強調したい場合に最適です。

</div>
<div class="col v-bottom text-right">

### 右下揃え
`v-bottom text-right`

垂直方向は下、水平方向は右に寄せられます。補足情報や注釈を配置する際などに活用できます。

</div>
</div>

---

<!-- _class: split-2 -->

# カラム内の配置指定 (split)

<div class="columns">
<div class="v-middle text-center">

### 中央配置
`v-middle text-center`

背景色や枠線がない `split` レイアウトでも、自由な位置指定が可能です。

</div>
<div class="v-top text-left">

### 通常配置
(デフォルト)

上寄せ・左寄せの標準的な配置です。他のカラムとの対比で位置を調整したい場合に便利です。

</div>
</div>

---

<!-- _class: v-center text-center -->

# スライド全体の中央揃え

`_class: v-center text-center`

このスライドのように、タイトルを含めたコンテンツ全体をスライドの中央に配置することも可能です。

特定のメッセージを強く印象付けたいスライドや、
セクションの合間のスライドに適しています。

---

<!-- _class: grid-quadrant -->


# 4象限分析

<div class="grid">
<div class="cell">

### 高影響 × 低コスト

- プロセスの標準化
- ドキュメント整備
- 定例会議の効率化

</div>
<div class="cell">

### 高影響 × 高コスト

- 基幹システム刷新
- AI/ML導入
- グローバル展開

</div>
<div class="cell">

### 低影響 × 低コスト

- UI微調整
- 社内ツール更新
- メール通知改善

</div>
<div class="cell">

### 低影響 × 高コスト

- レガシー完全移行
- 全拠点同時展開
- カスタム開発

</div>
</div>

---

<!-- _class: grid-sharp -->


# シャープグリッド（ボーダーのみ）

<div class="grid">
<div class="cell">

### フロントエンド

- React / TypeScript
- Tailwind CSS
- Vite

</div>
<div class="cell">

### バックエンド

- Node.js / Express
- PostgreSQL
- Redis

</div>
<div class="cell">

### インフラ

- AWS ECS
- CloudFront
- RDS

</div>
<div class="cell">

### 監視・運用

- CloudWatch
- Datadog
- PagerDuty

</div>
</div>

---

<!-- _class: timetable -->

# タイムテーブル

| 時間 | セッション | 担当 |
|------|------------|------|
| 10:00 - 10:30 | オープニング・挨拶 | 田中 |
| 10:30 - 11:30 | 基調講演 | 山田 |
| 11:30 - 12:00 | Q&A セッション | 全員 |
| 12:00 - 13:00 | 昼食休憩 | - |
| 13:00 - 14:30 | ワークショップ | 佐藤 |
| 14:30 - 15:00 | 振り返り・クロージング | 田中 |

---

<!-- _class: steps -->

# 導入ステップ

1. **要件定義**
   現状分析とゴール設定を行い、プロジェクトスコープを明確化
2. **設計・開発**
   アーキテクチャ設計とプロトタイプ開発を実施
3. **テスト・検証**
   総合テストとユーザー受入テストで品質を担保
4. **本番展開**
   段階的リリースと運用モニタリングを開始

---

<!-- _class: timeline -->

# プロジェクトの歩み

1. **2024年 Q1** プロジェクト発足、要件定義フェーズ開始
2. **2024年 Q3** プロトタイプ完成、ユーザーテスト実施
3. **2025年 Q1** ベータ版リリース、フィードバック収集
4. **2025年 Q3** 正式リリース、全社展開完了
5. **2026年 Q1** 機能拡張版リリース、海外展開開始

---

<!-- _class: checklist -->

# チェックリスト

リリース前の最終確認項目です。

- 要件定義書のレビュー完了
- 全体テストカバレッジ 80% 以上
- パフォーマンス要件のクリア
- ユーザーマニュアルの作成と承認
- セキュリティ診断の実施と指摘事項の改修

※ `checklist` クラスをスライドに付与するだけで、通常の箇条書きがチェックマーク付きのデザインになります。

---

<!-- _class: dense -->

# コールアウトとバッジ

汎用的に使えるハイライト要素です。新機能 <span class="badge danger">NEW</span> や、状態 <span class="badge success">完了</span> を表現できます。

<div class="callout info">
<h4>ℹ️ Information</h4>
標準のコールアウトです。補足情報やヒントを記載するのに適しています。
</div>

<div class="callout success">
<h4>✅ Success</h4>
成功や完了を伝えるメッセージです。ポジティブな結果を強調します。
</div>

<div class="callout warning">
<h4>⚠️ Warning</h4>
注意喚起です。仕様の制限や、気をつけるべきポイントを記載します。
</div>

<div class="callout danger">
<h4>🚨 Danger</h4>
重大な警告です。非推奨の操作や、エラー状態を表現するのに使用します。
</div>

---

<!-- _class: key-message no-pagination -->
<!-- _header: "" -->
<!-- _footer: "" -->

> DXは技術導入ではなく、
> ビジネス変革である。

テクノロジーは手段に過ぎない。真の変革は人と組織から始まる。

---

# コードブロック

インフラ構成をコードで管理：

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
  api:
    build: ./api
    environment:
      - DATABASE_URL=postgres://db:5432/app
```

---

<!-- _class: dense -->

# 文字の詰め込み（dense）

`_class: dense` を使用すると、フォントサイズや余白が調整され、標準よりも多くの情報を1枚のスライドに収めることができます。

### Denseクラスの特徴
- 基本フォントサイズを **20px** に縮小（標準は24px）
- 見出し（H1-H3）のサイズを最適化
- 行間や段落間の余白をタイトに調整
- リスト項目間の余白を削減

### 活用シーン
- 複数の要件定義を一覧表示したい場合
- 1つのトピックに対して補足説明が多い場合

> 引用ブロックのサイズも自動的に調整されます。
> これにより、デザインの統一感を保ったまま情報密度を高めることが可能です。

- **技術スタックの例**
  - フロントエンド: React, TypeScript, Next.js / バックエンド: Node.js, Python, Go
  - インフラ: Azure, AWS, GCP / データベース: PostgreSQL, Cosmos DB, Redis

---

<!-- _class: extra-dense split-2 -->

# 設計詳細 (1/2)：システム構成

`_class: extra-dense` は、さらに情報量を増やしたい場合に最適です。

<div class="columns">
<div>

### システム要件詳細
1. **可用性**: 年間稼働率 99.99% 以上を目標とする
2. **パフォーマンス**: 
   - APIレスポンス 200ms 以下
   - 同時接続数 10,000 以上
3. **セキュリティ**:
   - OAuth 2.0 / OIDC による認証
   - 通信および保存データの暗号化 (AES-256)
   - WAFによる脆弱性対策

</div>
<div>

### データ構造
- **User Entity**:
  - `id`: UUID (Primary Key)
  - `username`: String (Unique)
  - `roles`: Array<String>
- **Session Data**:
  - `token`: JWT
  - `expires_at`: Timestamp
- **Audit Logs**:
  - 誰が、いつ、どの操作を行ったかを全て記録

</div>
</div>

---

<!-- _class: extra-dense -->

# 設計詳細 (2/2)：詳細仕様

通常のスライドとしては文字が多すぎますが、ドキュメント的な役割を果たすスライド（配布資料など）において、情報の網羅性を担保するために使用してください。

### 導入テクノロジー
| 項目 | 詳細仕様 | 備考 |
|------|----------|------|
| 認証 | Azure AD B2C | 外部IDP連携を含む |
| 監視 | Azure Monitor | Application Insightsを併用 |
| CI/CD | GitHub Actions | 自動テストとセキュリティスキャン |
| DB | Cosmos DB | グローバル分散構成 |
| Cache | Redis | セッション管理に使用 |

### 運用保守体制
- 24時間365日の監視・通報体制
- 月次のセキュリティパッチ適用
- 半年ごとの災害復旧（DR）テスト

---

# テキスト装飾

**太字テキスト** で重要なポイントを強調できます。

*イタリック* で補足情報を示します。

<mark>ハイライト</mark> でさらに目立たせることも可能です。

> 引用ブロックは、重要な発言や参照元の情報を
> 視覚的に区別して表示するのに最適です。

インライン `コード` もスタイリング済みです。

---

# 画像の扱い：1枚のケース

![center shadow width:600px](./assets/sample_image.jpg)

中央寄せ (`center`) とドロップシャドウ (`shadow`) を適用した例です。

---

<!-- _class: cols-2 -->

# 画像の扱い：2枚のケース

<div class="columns">
<div class="col">

### セキュリティ

![width:100%](./assets/sample_image.jpg)

堅牢なセキュリティ基盤を提供します。

</div>
<div class="col">

### パフォーマンス

![width:100%](./assets/sample_image.jpg)

最高速の処理能力を実現します。

</div>
</div>

---

# テキストと画像の共存

![bg right:45% shadow](./assets/sample_image.jpg)

Marpの `bg` ディレクティブを使用することで、テキストと画像を左右に分割して配置できます。

- 背景画像として扱うためレイアウトが崩れにくい
- `left` や `right` で位置を簡単に指定可能
- 比率（例: `45%`）の調整も自由自在

ビジネスプレゼンテーションで最も多用されるレイアウトの一つです。

---

<!-- _class: grid-quadrant -->

# 4象限画像グリッド

<div class="grid">
<div class="cell side">
<div>

### クラウド基盤
スケーラブルなインフラを実現。
</div>

![width:200px](./assets/sample_image.jpg)
</div>

<div class="cell side">
<div>

### AI最適化
最新のアルゴリズムを統合。
</div>

![width:200px](./assets/sample_image.jpg)
</div>

<div class="cell side">
<div>

### データ分析
リアルタイムでの可視化を提供。
</div>

![width:200px](./assets/sample_image.jpg)
</div>

<div class="cell side">
<div>

### ユーザー体験
直感的な操作性を追求。
</div>

![width:200px](./assets/sample_image.jpg)
</div>
</div>

---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->

# ご清聴ありがとうございました

---

<!-- _class: profile -->

# プロフィール

<div class="profile-layout">
<div class="profile-image">

![width:200px](./assets/sample_image.jpg)

</div>
<div class="profile-content">

## 山田 太郎 (Taro Yamada)
**シニアエンジニア / プロジェクトリード**

- **所属**: テクノロジー推進部
- **専門**: クラウドアーキテクチャ、AI/MLシステム設計
- **経歴**: 大手SIer → スタートアップ → 現職（在籍5年）
- **資格**: AWS Solutions Architect、Azure Solutions Architect Expert

</div>
</div>
