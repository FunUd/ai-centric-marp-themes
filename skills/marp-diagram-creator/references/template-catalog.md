# スライド図解テンプレートカタログ (Slide Diagram Template Catalog)

本カタログは、スライド作成時に即座に利用できるプリセットテンプレートの一覧と、それぞれの特徴・適用シーンをまとめたものです。

---

## 1. Mermaid テンプレート (`scripts/diagrams/templates/mermaid/`)

| ファイル名 | タイプ | 推奨レイアウト | 用途・説明 |
|---|---|---|---|
| `flowchart-linear.mmd` | フローチャート | Full (全幅) | 横方向（左から右）へ進む標準的な業務・処理フロー。各ステップにアイコンや注記を追加可能。 |
| `flowchart-col2.mmd` | フローチャート | 2-Column (左右分割) | 上から下へ進む条件分岐付きフロー。開始・判定・終了の端点を備え、縦長スペースに最適。 |
| `sequence-api.mmd` | シーケンス図 | Full (全幅) | クライアント、API Gateway、認証、DB間のリクエスト/レスポンス往復。autonumber付き。 |
| `architecture-3tier.mmd` | アーキテクチャ図 | Full (全幅) | プレゼンテーション層、アプリケーション層、データ層の3層構造とサービス間連携。 |
| `state-machine.mmd` | 状態遷移図 | 2-Column / Full | 下書き、審査中、承認済、差戻し、公開中等のステートマシン遷移。 |

---

## 2. draw.io テンプレート (`scripts/diagrams/templates/drawio/`)

| ファイル名 | 推奨レイアウト | 用途・説明 | VS Code 再編集 |
|---|---|---|---|
| `system-architecture.drawio` | Full (全幅) | クライアント層、API層、データ層を上下に配置したスライド専用3層システム構成図。 | ○ (`hediet.vscode-drawio`) |
| `cloud-infrastructure.drawio` | Full (全幅) | クラウドVPC、DMZ/パブリックサブネット、プライベートコンテナクラスタ、RDS/Redisを網羅したインフラ図。 | ○ (`hediet.vscode-drawio`) |
| `comparison-matrix.drawio` | Full (全幅) | 2軸4象限（優先順位マトリクス、SWOT分析、施策対比）の標準レイアウト。 | ○ (`hediet.vscode-drawio`) |

## 3. JSON SVG テンプレート (`scripts/diagrams/templates/`)

| ファイル名 | タイプ | 推奨レイアウト | 用途・説明 |
|---|---|---|---|
| `charts/revenue-pie.json` | 円グラフ | Full / Col2 | 構成比の比較。 |
| `charts/revenue-donut.json` | ドーナツ | Full / Col2 | 中央指標付きの構成比。 |
| `concepts/team-pyramid.json` | ピラミッド | Full / Col2 | 成熟度・優先度などの積み上げ。 |
| `concepts/improvement-cycle.json` | 循環図 | Full / Col2 | 継続的改善や反復プロセス。 |
| `concepts/team-radial.json` | 放射状概念図 | Full / Col2 | 中心概念とカテゴリの関係。 |
| `timelines/product-roadmap.json` | タイムライン | Full | 時系列の計画と状態。 |
| `organization/team-org-chart.json` | 組織図 | Full | 階層と親子関係。 |

---

## 3. テーマ別スタイルの対応表

| テーマ | モード | 主要色 (Primary) | アクセント色 | 特徴 |
|---|---|---|---|---|
| **Azure Clarity** | ライト | `#2C7BE5` (Blue) | `#1B4F72` (Navy) | 信頼感のある王道ビジネスブルー。角丸ゼロでシャープ。 |
| **Crimson Clarity** | ライト | `#D32F2F` (Red) | `#5C0000` (Dark Red) | エネルギーと決断力のあるコーポレートレッド。 |
| **Prism Edge** | ライト | `#4F46E5` (Indigo) | `#06B6D4` (Cyan) | 洗練されたインディゴ＆シアン。モダンな幾何学感。 |
| **Nebula Glass** | ダーク | `#8B5CF6` (Violet) | `#22D3EE` (Cyan) | ダーク背景 (`#040712`) とネオン発光。サイバー感。 |
| **Warm Sunnyday** | ライト | `#FF8C42` (Orange) | `#6E3B3B` (Brown) | 親しみやすい暖色オレンジ。角丸大のやわらかいデザイン。 |
| **Slate Minimal** | ライト | `#475569` (Slate) | `#111111` (Ink Black) | 余計な装飾を削ぎ落としたミニマリスト・モノトーン。 |
