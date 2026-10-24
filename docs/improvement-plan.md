# 改善計画 (Improvement Plan) — AIスライド自動作成の利便性・品質向上

作成日: 2026-10-11 / 対象リポジトリ: `ai-centric-marp-themes`
根拠: リポジトリ全域（`themes/`、`skills/` 21種、`scripts/diagrams/`、`slides/sample-slide/`、`docs/`、`README.md`、`CHANGELOG.md`、`pyproject.toml`）の調査結果に基づく。

`docs/improvement-backlog.md` のP0〜P2は完了済み、P3（P3-1〜P3-4）は未着手。本計画はP3の具体化＋新規項目（DX / 品質 / Marp機能 / Skill内容）を扱う。**本ファイルが進捗管理の正本（SSoT）**。別エージェントが本ファイルだけ読んで実施できる粒度で記載する。

## 進捗管理ルール

- 各項目の状態は概要表の `状態` 列で管理する: `未着手` → `進行中` → `完了`。
- 作業開始時に `状態` を `進行中` に更新し、完了条件のチェックボックスをすべて満たしたら `完了` にする。
- 完了条件の `- [ ]` は実施者が `- [x]` に更新する。
- 1項目の作業が終わるごとに、下記「全体の完了ゲート」を実行し、パスしたらコミットする。

### 全体の完了ゲート（全項目共通、1項目完了ごとに実行）

```bash
python scripts/run-all-sync.py --check
python -m pytest scripts/diagrams/tests/ -q
python skills/marp-slide-creator/scripts/marp-lint.py slides/sample-slide/<変更に関係する>-sample.md
```

> skills配下を変更したら `python scripts/sync-skills.py` を実行して各エージェント向けミラーに同期すること（忘れるとCIが失敗する）。図版エンジンを変更したら `python scripts/sync-skill-vendor.py`、トークンを変更したら `sync-tokens-from-css.py` / `sync-theme-classes.py` も実行。詳細は `README.md` の Project Structure 節参照。

## 概要表

| ID | 優先度 | 項目名 | 主な対象ファイル | 状態 | 効果/工数 |
|---|---|---|---|---|---|
| A-1 | P1（高） | スターター構成の同梱＋`setup-slide-project.py`強化 | `skills/marp-slide-creator/scripts/setup-slide-project.py`、`slides/starter-template.md`（新規）、`.vscode/extensions.json`（新規）、`marp.config.example.js`（新規） | 完了（2026-10-11） | 大/小 |
| A-2 | P2（中） | GitHub Pagesプレビュー自動公開 | `.github/workflows/pages.yml`（新規）、`scripts/take-screenshots.py` | 未着手 | 大/中 |
| A-3 | P2（中） | Standalone配布の自動化（フォント同梱zip） | `.github/workflows/release.yml`（新規）、`package.json` | 未着手 | 中/中 |
| A-4 | P3（低） | 図版JSONスキーマ追加 | `scripts/diagrams/schemas/`（新規）、`.vscode/settings.json` | 未着手 | 中/小 |
| A-5 | P3（低） | 新規テーマ用視覚回帰テスト | `scripts/diagrams/tests/test_visual_regression.py`（新規） | 未着手 | 中/大 |
| B-1 | P1（高） | スキルルーティング単純化（入口集約） | `AGENTS.md`（新規）または`skills/marp-slide-creator/SKILL.md`、`README.md` Skill Routing節 | 未着手 | 大/小 |
| B-2 | P1（高） | Fast path / Full path分離＋差分再レンダー手順 | `skills/marp-slide-creator/SKILL.md` | 未着手 | 大/小 |
| B-3 | P2（中） | 入力ドキュメント→スライド変換ガイド | `skills/slide-content-designer/SKILL.md`、`skills/slide-content-designer/references/quality-guidelines.md` | 未着手 | 大/中 |
| B-4 | P2（中） | エラー別修正パッチ例集（日） | `skills/marp-slide-creator/references/marp-syntax-guide.md` | 未着手 | 中/小 |
| C-1 | P1（高） | 文章品質lint（文字数・箇条書き・汎名詞見出し） | `skills/marp-slide-creator/scripts/marp-lint.py`、`scripts/diagrams/tests/test_marp_lint.py` | 未着手 | 大/中 |
| C-2 | P1（高） | 表・コード・脚注パターン整備＋lint | `skills/marp-slide-creator/SKILL.md`、`skills/marp-slide-creator/scripts/marp-lint.py`、`docs/classes.md`、`themes/*.css` | 未着手 | 大/中 |
| C-3 | P2（中） | 狭レイアウト図版テンプレ拡充 or lint誘導強化 | `scripts/diagrams/templates/mermaid/`、`scripts/diagrams/check-templates.py`、`skills/marp-slide-creator/scripts/marp-lint.py`、`docs/diagrams.md` | 未着手 | 中/中 |
| C-4 | P2（中） | 英語長語wrap改善＋legend誘導 | `scripts/diagrams/renderers/`、`scripts/diagrams/tests/`、`skills/marp-diagram-creator/references/diagram-patterns.md` | 未着手 | 中/中 |
| C-5 | P2（中） | テーマ別禁止組み合わせ表の集約 | `skills/theme-expert-common/SKILL.md` | 未着手 | 中/小 |
| C-6 | P3（低） | アイコン自動再色＋auto-fix提案 | `skills/marp-svg-icon-placer/scripts/`、`skills/marp-slide-creator/scripts/marp-lint.py` | 未着手 | 小/中 |
| D-1 | P1（高） | `marp-syntax-guide.md` 追記（html/数式/notes/メタ） | `skills/marp-slide-creator/references/marp-syntax-guide.md` | 未着手 | 大/小 |
| D-2 | P2（中） | Fragment対応可否の明記 | `skills/marp-slide-creator/references/marp-syntax-guide.md`、`skills/marp-slide-creator/scripts/marp-lint.py` | 未着手 | 小/小 |
| D-3 | P2（中） | グローバル調整系directiveの許可/禁止線引き | `skills/marp-slide-creator/references/marp-syntax-guide.md` | 未着手 | 小/小 |
| E-1 | P2（中） | `slide-expert-*` にレイアウト対応表＋図版対応表 | `skills/slide-expert-*/SKILL.md`（9種） | 未着手 | 中/中 |
| E-2 | P2（中） | `theme-expert-*` の加筆（カバー選定＋NG例） | `skills/theme-expert-*/SKILL.md`（6種＋common） | 未着手 | 中/中 |
| E-3 | P3（低） | `theme-creator` 足場生成スクリプト | `scripts/setup-theme-project.py`（新規）、`skills/theme-creator/SKILL.md` | 未着手 | 小/中 |

---

## A. リポジトリ・配布改善

### A-1: スターター構成の同梱＋`setup-slide-project.py`強化（P3-3の具体化）

- **背景**: 現状 `setup-slide-project.py` は空の `slides/<name>/assets/` を作るだけ（`create_project()` はmkdirのみ）。新規利用者はREADMEの手順（テーマCSS手動コピー、`assets/fonts/`ミラー、frontmatter記述）を毎回手作業し、AIも雛形なしで書き始めるため初手ミスが多い。`docs/improvement-backlog.md` P3-3の具体化。
- **対象ファイル**:
  - `skills/marp-slide-creator/scripts/setup-slide-project.py`（改修）
  - `slides/starter-template.md`（新規）
  - `.vscode/extensions.json`（新規、推奨: `marp-team.marp-vscode`）
  - `marp.config.example.js`（新規、`themeSet` 設定例）
- **実装手順**:
  1. `setup-slide-project.py` に `--theme <theme-name>` 引数を追加（既定 `azure-clarity`、6テーマ名のみ受理、不正値はエラー終了）。
  2. `create_project()` を拡張し、以下を自動生成する:
     - `slides/<name>/<name>.md`（後述スターターの複製。frontmatterの `theme:` は指定テーマ）
     - `slides/<name>/themes/<theme>.css`（`themes/<theme>.css` の複製）
     - `slides/<name>/assets/fonts/`（`assets/fonts/` のうち当該テーマが `@font-face` で参照するファイルのみ複製。参照判定は `tests/test_fonts_manifest.py` のロジックを流用。azure/crimsonはコピー不要）
     - `slides/<name>/assets/diagrams/.gitkeep`
  3. `slides/starter-template.md` を新規作成。frontmatterに `marp/html/lang/title/description/paginate/header/footer` を含め、cover・`cols-2`・`grid-quadrant`・`steps` 各1枚の最小例＋Presenter notes例を収録（D-1のメタ項目と整合させる）。
  4. `.vscode/extensions.json` に `marp-team.marp-vscode` を recommendations として追加。
  5. `marp.config.example.js` に `themeSet: ["./themes/"]` 例を記載。
  6. `README.md` Quick Start節に生成コマンドを追記。
- **完了条件**:
  - [x] `python skills/marp-slide-creator/scripts/setup-slide-project.py my-deck --theme prism-edge` で上記4種が生成されること（deck＋themes＋fonts 8/8＋diagrams/.gitkeepを確認）
  - [x] 生成直後のdeckが `marp-lint.py` exit 0 かつ `post-edit-check.py --expect <N>` exit 0 であること（prism-edge/nebula生成deckで確認、N=5）
  - [x] `--theme bogus` が非ゼロ終了すること（argparse choicesによりexit 2を確認）
  - [x] 全体の完了ゲートがパスすること（`run-all-sync.py --check`、`ruff check/format`、pytest全件パスを確認。2026-10-11）
- **実施記録 (2026-10-11)**:
  - `setup-slide-project.py` を `--theme` 対応に全面改修（既定azure-clarity、不正値はchoicesで拒否、既存deckへの上書き拒否exit 1、フォント判定は `test_fonts_manifest.py` と同一正規表現、`compat.ensure_utf8_stdio` 準拠）。
  - `slides/starter-template.md`（5スライド: cover/cols-2/grid-quadrant/steps/key-message＋presenter notes例）は `marp-lint.py` フルモード・`--structural-only`・`post-edit-check.py --expect 5 --lang ja` のすべてでクリーン。
  - 追加の検証: nebula-glass生成でfonts 9/9、azure既定でfonts 0件、3種ともfrontmatter `theme:` 置換OK。検証用3deckは削除済み。
  - `README.md`（Quick Start §5、構成ツリー、`setup-slide-project.py` 説明文）、`CHANGELOG.md` Unreleasedに追記。`sync-skills.py` で全ミラー同期済み。

### A-2: GitHub Pagesプレビュー自動公開（P3-2の具体化）

- **背景**: テーマ選定時に実物スライドを見られず、READMEの静止画のみが頼り。`take-screenshots.py` の成果物とHTMLビルドをPagesに載せれば選定摩擦が大幅に下がる。
- **対象ファイル**: `.github/workflows/pages.yml`（新規）、`scripts/take-screenshots.py`（参照のみ、改修不要のはず）
- **実装手順**:
  1. `pages.yml` を新規作成。triggerは `push to main` かつ `themes/`・`slides/sample-slide/`・`scripts/take-screenshots.py` 変更時＋手動dispatch。
  2. ジョブ内容: Node setup（`package.json` のpin版）→ `npx @marp-team/marp-cli` で `slides/sample-slide/*-sample.md` を `--theme` 指定でHTML化 → `assets/screenshots/` と併せて `gh-pages` ブランチ相当のartifactに配置 → `actions/deploy-pages` で公開。
  3. `themes/_base.css` は `--theme-set` に含めない（README既知のbenign WARN回避。`marp-syntax-guide.md` のNotes参照）。
- **完了条件**:
  - [ ] ワークフローがmain pushで成功し、6テーマのHTML＋操作可能なスライドショーが公開URLで閲覧できること
  - [ ] `themes/*.css` 変更→pushでプレビューが自動更新されること

### A-3: Standalone配布の自動化（P3-1の具体化）

- **背景**: README Quick Start手順2（CSS＋fonts手動コピー）が初学者・AI双方の負担。Release時にフォント同梱zipを自動生成すれば解消する。
- **対象ファイル**: `.github/workflows/release.yml`（新規）、`package.json`（参照）
- **実装手順**:
  1. タグpush（`v*`）で起動するワークフローを作成。
  2. `themes/<theme>.css`＋当該テーマ必要フォント＋`starter-template.md`＋`marp.config.example.js` をzip化（テーマ別6zip＋all-in-one 1zip）。
  3. GitHub Releaseに添付。
- **完了条件**:
  - [ ] テストタグでzipが生成され、展開直後にMarpプレビューできること（fonts 404なし）

### A-4: 図版JSONスキーマ追加

- **背景**: `templates/charts|concepts|organization/*.json` のtypo（`type`名、`series`構造等）はレンダー時まで検出できない。AI生成JSONのミス率を下げる。
- **対象ファイル**: `scripts/diagrams/schemas/diagram.schema.json`（新規）、`.vscode/settings.json`（json.schemas追記）
- **実装手順**:
  1. `DIAGRAM_TYPES`（`scripts/diagrams/diagram_models.py`）を正として、全typeの必須/任意フィールドをスキーマ化。`aspect` と `height` の相互排他も `not.required` で表現。
  2. `.vscode/settings.json` に `$schema` マッピングを追加。
  3. `render-slide-diagram.py` のJSON読み込み直後にスキーマ簡易検証（stdlibのみ。`jsonschema` 依存は追加しない。必須キー存在チェック＋相互排他チェックで十分）を追加し、違反時はフィールド名付きエラー＋exit非ゼロ。
- **完了条件**:
  - [ ] 不正JSON（未知type、`aspect`+`height`併用、必須欠落）が humano-readable エラーで非ゼロ終了すること
  - [ ] 既存14テンプレートが全て検証パスすること
  - [ ] pytestに3件以上の回帰テストを追加しパスすること

### A-5: 新規テーマ用視覚回帰テスト

- **背景**: `_base.css` 変更の影響を現状CIは構造テストのみで担保し、見た目差分は検出できない。
- **対象ファイル**: `scripts/diagrams/tests/test_visual_regression.py`（新規）
- **実装手順**:
  1. Playwright導入済み前提で、`slides/sample-slide/*-sample.md` の先頭N枚をHTML化→スクリーンショット→前回ゴールデン（`assets/screenshots/`）とピクセル比較（許容誤差付き）。
  2. フォントメトリクス差異による環境差（CHANGELOG既知のmermaid fixtures drift）を踏まえ、初版は `azure-clarity` cover＋tocのみ等、狭い範囲で開始。
- **完了条件**:
  - [ ] 意図的なCSS変更なしでパスし、意図的な色変更で失敗すること
  - [ ] CIのubuntuジョブに組み込まれること（失敗時はсыз差分画像をartifact upload）

---

## B. AI自動作成の利便性

### B-1: スキルルーティング単純化（入口集約）

- **背景**: 21スキル＋README Skill Routing 8段階（README:214-228）はAIの選択ミスを誘発する（planning/impl混同が最多）。
- **対象ファイル**: `AGENTS.md`（新規、リポジトリ直下）／代替案として `README.md` Skill Routing節の改訂でも可。どちらか一方のみ実施。
- **実装手順**:
  1. `AGENTS.md` を新規作成。内容は判定木のみに絞る（各スキルの重複説明は書かない）:
     - outline未確定 → `slide-content-designer`（＋該当 `slide-expert-*` 併読）
     - outline確定済み → `marp-slide-creator`
     - 図が必要 → `marp-diagram-creator`
     - アイコン → `marp-svg-icon-placer`
     - テーマ固有の磨き → 該当 `theme-expert-*`（`theme-expert-common` は単独起動禁止）
     - 新規テーマ → `theme-creator`
  2. 各 `slide-expert-*/SKILL.md` のdescriptionはplanning限定の旨を維持し、`AGENTS.md` からリンクする。
  3. `scripts/sync-skills.py` の同期対象に `AGENTS.md` を含めるか判断し、含める場合はスクリプト改修＋テスト更新、含めない場合は本計画書に理由を記録。
- **完了条件**:
  - [ ] 新規セッションでAIに「スライドを作りたい」とだけ依頼した際、本ファイル/AGENTS.mdのみで正しい第一スキルに到達できること（目視確認）
  - [ ] 既存スキルdescriptionと矛盾しないこと

### B-2: Fast path / Full path分離＋差分再レンダー手順

- **背景**: `marp-slide-creator/SKILL.md` §4の9段階フルループは品質は高いが、下書き反復では重い（全PNG再生成＋全読）。トークン浪費の主因。
- **対象ファイル**: `skills/marp-slide-creator/SKILL.md`
- **実装手順**:
  1. §4冒頭に分岐を追加:
     - **Fast path（下書き）**: post-edit-check → marp-lint → marp-diagnostics（DOMのみ）。画像生成なし。
     - **Full path（納品前）**: Fast path通過後にStage 4（`marp-cli --images png` 単一パイプライン＋全画像一括一読）。
  2. 差分手順を追記: 修正後は全スライドでなく変更スライド番号のみ再生成・再読し、ファイル数≠スライド数の検証（Stage 4 Step 1の既存手順）は維持。
  3. 二重パイプライン禁止（`--screenshot-dir` 併用禁止）の既存警告は両pathに残す。
- **完了条件**:
  - [ ] Fast/Fullの切替条件がif-then形式で明記されていること
  - [ ] `sync-skills.py` 実行＋ `--check` パス

### B-3: 入力ドキュメント→スライド変換ガイド

- **背景**: `slide-content-designer` は白紙ヒアリング専用で、実務で多い「論文・議事録・CSV→叩き台」手順がない。
- **対象ファイル**: `skills/slide-content-designer/SKILL.md`、`skills/slide-content-designer/references/quality-guidelines.md`
- **実装手順**:
  1. `SKILL.md` §5に「入力持ち込み時」分岐を追加:
     - 長文→各スライド200-350字に圧縮、溢れ分はpresenter notes送り
     - 表・数値→JSON chart候補（`bar/line/stacked-bar/pie/donut`）への割付基準（時系列→line、構成比→pie/donut、比較→bar）
     - 図の事前指定をoutlineに含める（スライド番号＋使用テンプレ名＋layout）
  2. `quality-guidelines.md` にCSV見出し→JSON `categories/series` 対応例を最小1例追記。
- **完了条件**:
  - [ ] サンプルCSV1件→JSON chart→embedまで本ガイドのみで到達できること
  - [ ] `sync-skills.py --check` パス

### B-4: エラー別修正パッチ例集（日）

- **背景**: lint/validatorのメッセージは英語で、JP利用者の修正往復が多い。
- **対象ファイル**: `skills/marp-slide-creator/references/marp-syntax-guide.md`（末尾に §6 として追加）
- **実装手順**: 頻出5件について「エラー文→原因→修正前後の最小diff」の定型表を追加: `DIAGRAM_OVERFLOW_WIDTH`、`DIAGRAM_MISSING_WIDTH`、`CENTERED_LIST`、`MISSING_CLASS_DIRECTIVE`、`OVERSIZED_ICON`。
- **完了条件**:
  - [ ] 5件すべてに修正前/後のmarkdown断片があること
  - [ ] `sync-skills.py --check` パス

---

## C. 生成スライドの品質向上

### C-1: 文章品質lint（文字数・箇条書き・汎名詞見出し）

- **背景**: So What?見出し・Bold Key Labels・Magic Number 3はprose指導のみ。`DENSE_CONTENT` 閾値（400）と推奨（200-350）の乖離も既知。
- **対象ファイル**: `skills/marp-slide-creator/scripts/marp-lint.py`、`scripts/diagrams/tests/test_marp_lint.py`、`skills/marp-slide-creator/scripts/theme-classes.json`（必要時のみ再生成）
- **実装手順**:
  1. WARNING 3種を追加（いずれも既定ON、ERRORにしない）:
     - `DENSE_BODY`: 本文合計350字超（notes送り提案。現行400閾値のメッセージと定数を本値に統一）
     - `MANY_BULLETS`: 1スライド箇条書き5件超（layout別上限は既存 `_slide_layout_key()` を流用）
     - `GENERIC_TITLE`: 見出しが `概要|アジェンダ|概要紹介|Architecture|Overview|Status|Next Steps` 等の汎名詞のみ（大文字小文字不問、前後空白許容）
  2. 各チェックに単体テスト（正常系＋near-miss）を追加。
  3. `SKILL.md` §7チェックリストに3項目を反映。
- **完了条件**:
  - [ ] `test_marp_lint.py` 新規テストがすべてパスし、既存138件が壊れないこと
  - [ ] サンプル6deckが新規WARNINGゼロであること（出たらdeck修正か閾値見直し。無闇に除外リストを増やさない）
  - [ ] `sync-theme-classes.py --check` パス（manifest変更時のみ）

### C-2: 表・コード・脚注パターン整備＋lint

- **背景**: 表は `timetable` のみ文書化、コードは「短く」のみ、出典脚注パターンなし。ワイドテーブル・長コードがoverflowの常習犯。
- **対象ファイル**: `skills/marp-slide-creator/SKILL.md`（§6に追記）、`skills/marp-slide-creator/scripts/marp-lint.py`、`docs/classes.md`（必要時のみ）、`themes/*.css`（必要時のみ。原則CSS変更なしで完結させる）
- **実装手順**:
  1. SKILL §6に優先順位付き対処を追加: 列削減→フォント縮小（scoped）→縦積み/分割→notes送り。コードは「20行or800字超は分割かnotes」の目安を明記。
  2. 脚注パターンを1つ制定（例: スライド末尾 `出典: ...` の `text-small text-sub` 行）し、SKILLに例示。
  3. lintにWARNING 2種: `WIDE_TABLE`（列数7超または1セル40字超の行あり）、`LONG_CODE`（コードブロック20行超）。いずれも分割提案メッセージ付き。
- **完了条件**:
  - [ ] 新規WARNING 2種の単体テストがパスすること
  - [ ] サンプル6deckが新規WARNINGゼロであること
  - [ ] 全体の完了ゲートがパスすること

### C-3: 狭レイアウト図版テンプレ拡充 or lint誘導強化

- **背景**: Gantt/ER等は `full` のみ（`docs/diagrams.md` 対応表）。AIが `col2` に無理やり載せて潰す事故あり。
- **対象ファイル**: `scripts/diagrams/templates/mermaid/`、`scripts/diagrams/check-templates.py`（`ALLOWED_LAYOUTS`）、`skills/marp-slide-creator/scripts/marp-lint.py`、`docs/diagrams.md`
- **実装手順**（いずれか一方を選択し、本ファイルに選択を記録）:
  - 案X（推奨・小）: lintに `DIAGRAM_FULL_ONLY_IN_COLUMN`（full専用テンプレ由来SVGをcol系layoutでembedしたらWARNING）を追加。テンプレ由来判定はファイル名辞書で十分。
  - 案Y（大）: Gantt/ERの `col2/asym` 版テンプレを追加し `ALLOWED_LAYOUTS`＋対応表を更新。
- **完了条件**:
  - [ ] 選択案のテスト（案X: lint単体テスト / 案Y: `check-templates.py` パス＋対応表更新）が通ること

### C-4: 英語長語wrap改善＋legend誘導

- **背景**: 軸ラベル8字ハードwrapで英単語が途中切断（`docs/diagrams.md` 注意書き）。見た目の安っぽさの主因。
- **対象ファイル**: `scripts/diagrams/renderers/*`（該当renderer）、`scripts/diagrams/tests/`、`skills/marp-diagram-creator/references/diagram-patterns.md`
- **実装手順**:
  1. wrapを通路境界優先（空白・ハイフン・CJK境界）に変更し、不可分語のみハードwrap＋ハイフン付与。
  2. ラベルが予算超（cartesian: full≤8/asym≤6/col2≤5/col3≤4）の場合は省略＋legend誘導のWARNING文を改善（現行の可読予算メッセージを流用）。
  3. ゴールデンfixtureへの影響を確認し、変化分は `regenerate-golden.py` で再生成＋目視。
- **完了条件**:
  - [ ] `Pinecone` 等の英単語が語中で切断されないこと（テスト追加）
  - [ ] ゴールデンテストがパスすること

### C-5: テーマ別禁止組み合わせ表の集約

- **背景**: 禁止事項が各skillに散在（icon再色はicon-placer、focus例外はREADME、callout同系色はslide-creator §9）。
- **対象ファイル**: `skills/theme-expert-common/SKILL.md`（§末尾に「禁止組み合わせ表」追加）
- **実装手順**: 最低6行の表を追加: centered系×リスト、`cols-*`×同系callout、nebula×未再色icon、catalog icon 200px超、`bg-dark` のprism以外使用、cover系×図版中央配置。各行に「代替案」列を付ける。詳細は既存skillへのリンクに留め、重複記述しない。
- **完了条件**:
  - [ ] 表の各行が既存lint項目または既存skill節に到達できること
  - [ ] `sync-skills.py --check` パス

### C-6: アイコン自動再色＋auto-fix提案

- **背景**: Phosphor 54種・手動copy→recolorの2手間。nebulaでの黒潰れが常習。
- **対象ファイル**: `skills/marp-svg-icon-placer/scripts/copy-icons.py`（または新規ラッパー）、`skills/marp-slide-creator/scripts/marp-lint.py`
- **実装手順**:
  1. `copy-icons.py` に `--theme` 引数を追加。`nebula-glass` 指定時は `#67E8F9` 系の明色へ自動再色（既存 `recolor-icons.py` の流用）。
  2. `OVERSIZED_ICON` エラーメッセージに推奨修正（`width:48px` 以下への書換え例）を付記。
- **完了条件**:
  - [ ] `--theme nebula-glass` コピー直後のSVGがダーク背景で可視（目視1件）であること
  - [ ] 既存テスト＋ゲートがパスすること

---

## D. Marp機能の未活用穴埋め

### D-1: `marp-syntax-guide.md` 追記（html/数式/notes/メタ）

- **背景**: 現行guideはdirectives・画像・exportのみ。AIが幻覚しやすい未文書領域が残る。
- **対象ファイル**: `skills/marp-slide-creator/references/marp-syntax-guide.md`（§4として追記。既存§4 Quick Referenceは§5へ繰下げ）
- **実装手順**: 各5〜15行で以下を追記し、 unsupported は unsupported と明記:
  1. `html: true`（VS Code拡張設定とCLI `--html` の両方。divレイアウトの前提条件）
  2. 数式（KaTeX/MathJax有効化frontmatter＋ `$...$` 例。slate-minimal想定）
  3. Presenter notes運用（溢れ文のnotes送り基準＋ `--pdf-notes` 使い分け）
  4. メタfrontmatter（`title/description/author/keywords/image/lang`。A-1のstarterと同一項目）
  5. `paginate: hold`、`size`、`backgroundColor` の用途限定メモ
- **完了条件**:
  - [ ] 各項目に最小動作例または「非対応」の明記があること
  - [ ] A-1のstarter-templateと項目名が一致していること
  - [ ] `sync-skills.py --check` パス

### D-2: Fragment対応可否の明記

- **背景**: 段階表示の可否が文書になく、AIが存在しない記法を捏造する恐れ。
- **対象ファイル**: `skills/marp-slide-creator/references/marp-syntax-guide.md`、`skills/marp-slide-creator/scripts/marp-lint.py`（任意）
- **実装手順**:
  1. 検証済みの可否をD-1追記内に1項として明記（可なら記法、不可なら代替＝分割スライド）。
  2. 不可の場合、幻覚記法（例: `<!-- fragment -->`）を検出するWARNINGを検討。確証がなければlint追加は見送り、本ファイルに理由を記録。
- **完了条件**:
  - [ ] 可否と代替手段が文書化されていること

### D-3: グローバル調整系directiveの許可/禁止線引き

- **背景**: `style` グローバル・scoped `<style>` の乱用がデザイン崩壊の元。現状 `--font-scale` のみ言及。
- **対象ファイル**: `skills/marp-slide-creator/references/marp-syntax-guide.md`
- **実装手順**: 許可（per-slide `font-size` 縮小、`table` 縮小等 §6既存）／原則禁止（グローバル `style:` での色・余白上書き、複数スライドに跨るscoped乱用）を表で明記。禁止破りが必要な場合は `theme-creator` 経由（CSS改修）へ誘導。
- **完了条件**:
  - [ ] 許可/禁止がif-thenで読めること
  - [ ] `sync-skills.py --check` パス

---

## E. Skill内容の個別強化

### E-1: `slide-expert-*` にレイアウト対応表＋図版対応表

- **背景**: 9種ともplanning-onlyで、実装時にどの `_class`・どの図テンプレを使うかが落ちる。ハンドオフ先の `marp-slide-creator` で毎回再判断になる。
- **対象ファイル**: `skills/slide-expert-*/SKILL.md`（9種すべて）
- **実装手順**:
  1. 各SKILL末尾（Workflow Handoff前）に2表を各5行程度で追加:
     - 節→レイアウト表（例: 比較表→`cols-2`＋表、推奨→`key-message`）
     - 節→図版表（例: tech-selection比較→JSON `matrix`、工程→`steps`+`arrows` or mermaid flowchart）
  2. 既存のDiagram Warning（tech-selectionにあるinline-Mermaid禁止の注意）の有無を9種で統一（なければ追加、あれば文面統一）。
  3. 不足ドメイン（営業・投資家・学術・オンボーディング）は本計画では追加しない。必要になったら別項目化すること。
- **完了条件**:
  - [ ] 9種すべてに2表があること
  - [ ] テンプレ名が `docs/diagrams.md` 対応表と一致していること
  - [ ] `sync-skills.py --check` パス

### E-2: `theme-expert-*` の加筆（カバー選定＋NG例）

- **背景**: `theme-expert-prism-edge` 27行等、薄い。カバー変種の使い分け条件・NG例がなく `theme-expert-common` 頼み。
- **対象ファイル**: `skills/theme-expert-<6theme>/SKILL.md`
- **実装手順**:
  1. 各テーマに「カバー選定3条件」（例: prism: Wave=躍動、Diagonal=変革、Noir=重厚、Aurora=未来）を5行以内で追加。
  2. 各テーマにNG例1件（例: nebula=未再色icon、slate=多色callout、warm=青系上書き）を追加。C-5の集約表と重複記述せず、集約表へリンク。
  3. 30-50行の簡潔さ（`theme-creator` §3.2の指針）は維持。肥大化させない。
- **完了条件**:
  - [ ] 6種すべてに選定条件＋NG例があること
  - [ ] `sync-skills.py --check` パス

### E-3: `theme-creator` 足場生成スクリプト

- **背景**: `theme-creator` Phase 2-6は手動6ステップで漏れやすい（skill・sample・docs・tokens・fonts・sync）。
- **対象ファイル**: `scripts/setup-theme-project.py`（新規）、`skills/theme-creator/SKILL.md`（Phase記載の更新）
- **実装手順**:
  1. `scripts/setup-theme-project.py <theme-name> --base azure-clarity --prefix nt` を新規作成。CSS雛形（必須セクション見出し＋`<base:name>` マーカー登録案内）、`skills/theme-expert-<name>/SKILL.md` 雛形、sample雛形を生成。
  2. 生成後に走らせる検証コマンド列（lint→tokens sync→class-docs→pytest→screenshots登録）をスクリプト末尾に表示。
  3. `theme-creator` SKILLに本スクリプトへの言及を追加。
- **完了条件**:
  - [ ] 生成直後のCSSが必須6ルール（`theme-creator` §2.2）を満たすこと
  - [ ] 全体の完了ゲートがパスすること

---

## 実施順の推奨

工数小・効果大から着手する: **A-1 → D-1 → C-1 → B-2 → B-4 → C-2 → E-1 → E-2 → B-1/B-3 → C-3/C-4/C-5 → A-2/A-3/A-4 → C-6/A-5/E-3**。
