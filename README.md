# AI Coding Skills Template

GitHub Copilot の Instructions / Skills を活用した、Python / Django 開発向けの AI コーディングルールテンプレート。

## 概要

このリポジトリは、GitHub Copilot に一貫したコーディング規約・開発プロセスを適用するためのテンプレートです。

### 目的

- Copilot に一貫したコーディング規約を適用する
- TDD（テスト駆動開発）を厳格に適用するワークフローを構築する
- CI/CD でコード品質を自動的に担保する
- Python / Django 開発のベストプラクティスを AI コーディング支援に組み込む

### 設計思想

Claude Code の [Superpowers](https://github.com/jamiecurnow/superpowers) プラグインの思想（特に「テストのない実装コードは破棄する」TDD 厳格方針）を、Copilot Instructions 向けに転用・再構成しています。

## プロジェクト構成

```
copilot-instructions-template
│
├── .github/
│   ├── copilot-instructions.md               # 全体共通ルール
│   │
│   ├── instructions/                         # 言語・フレームワーク別ルール
│   │   ├── python.instructions.md            # Python コード構成・命名・型・リソース管理
│   │   ├── python-patterns.instructions.md   # テスト・パフォーマンス・アンチパターン
│   │   ├── python-async.instructions.md      # 非同期・例外設計・バッチ処理
│   │   ├── python-pandas.instructions.md     # pandas コード品質・基本イディオム
│   │   ├── python-pandas-performance.instructions.md  # pandas パフォーマンス・大規模データ
│   │   ├── python-openpyxl.instructions.md   # openpyxl ベストプラクティス・Excel 操作
│   │   ├── python-logging.instructions.md    # ロギング・構造化ログ
│   │   ├── python-configuration.instructions.md  # 設定管理・環境変数・シークレット
│   │   ├── python-security.instructions.md   # セキュリティ・脆弱性防止
│   │   ├── python-documentation.instructions.md  # ドキュメント生成・Sphinx
│   │   ├── python-pyproject.instructions.md  # pyproject.toml・ツール構成
│   │   ├── django.instructions.md            # モデル設計・クエリ最適化・ビュー・Signals
│   │   ├── django-api.instructions.md        # DRF シリアライザー・認証・テスト
│   │   ├── django-infra.instructions.md      # マイグレーション・API 設計
│   │   └── django-celery.instructions.md     # Celery タスク設計・リトライ・冪等性
│   │
│   ├── skills/                               # プロセス・手順の知識（オンデマンド）
│   │   ├── tdd/SKILL.md                      # テスト駆動開発の手順
│   │   ├── code-review/SKILL.md              # PR レビューの手順
│   │   ├── refactoring/SKILL.md              # リファクタリング手順
│   │   └── debugging/SKILL.md                # デバッグ手順
│   │
│   └── workflows/                            # GitHub Actions
│       └── ci.yml                            # ruff + pytest + カバレッジ
│
├── examples/                                 # サンプルプロジェクト（実例）
│   ├── python-pandas/                        # Python + pandas による CSV データ分析
│   │   ├── pyproject.toml
│   │   ├── src/analyzer/                     # ソースコード
│   │   └── tests/                            # テストコード
│   │
│   └── django-app/                           # Django によるタスク管理 API
│       ├── pyproject.toml
│       ├── manage.py
│       ├── config/                           # Django 設定
│       ├── tasks/                            # タスク管理アプリ
│       └── tests/                            # テストコード
│
├── .claude/                                  # 参考資料（Superpowers Skills 等）
│   └── references/                           # 収集したスキル・調査結果
│
└── README.md
```

## 技術スタック

| カテゴリ | ツール | 用途 |
|----------|--------|------|
| Python | Python 3.12 | 実行環境 |
| パッケージ管理 | uv | 依存関係管理・仮想環境 |
| フォーマッター / リンター | ruff | コード整形・静的解析 |
| テスト | pytest | テスト実行 |
| カバレッジ | pytest-cov | テストカバレッジ計測 |
| Web フレームワーク | Django 5.x | Django サンプル用 |
| API フレームワーク | Django REST Framework | Django サンプル用 |
| データ分析 | pandas | Python サンプル用 |
| CI | GitHub Actions | 自動テスト・リント |
| PR レビュー | GitHub Copilot Code Review | 自動コードレビュー（ブランチルールセットで設定） |

## 使い方

### 1. テンプレートとして使用

```bash
# リポジトリをクローン
git clone https://github.com/<your-org>/copilot-instructions-template.git

# 自プロジェクトに必要なファイルをコピー
cp -r .github/copilot-instructions.md <your-project>/.github/
cp -r .github/instructions/ <your-project>/.github/
cp -r .github/skills/ <your-project>/.github/
cp -r .github/workflows/ <your-project>/.github/
```

### 2. カスタマイズ

- `.github/copilot-instructions.md` — 全体共通ルールを現場に合わせて編集
- `.github/instructions/` — 使用する言語・フレームワークに合わせて追加・削除
- `.github/skills/` — 必要なスキルを追加・編集
- `.github/workflows/ci.yml` — カバレッジ閾値等をプロジェクトに合わせて調整

## Copilot Instructions の構成

### copilot-instructions.md（全体共通）

すべてのファイルに適用される基本ルール：TDD 方針、コードスタイル、Git 規約、セキュリティ等。

### instructions/（言語・フレームワーク別）

`applyTo` で対象ファイルを指定し、言語・フレームワーク固有のルールを適用（各4,000文字以内）：

**Python 共通:**
- **python.instructions.md** — コード構成・命名・型・リソース管理
- **python-patterns.instructions.md** — テスト・パフォーマンス・アンチパターン
- **python-async.instructions.md** — 非同期・例外設計・バッチ処理
- **python-logging.instructions.md** — ロギング・構造化ログ
- **python-configuration.instructions.md** — 設定管理・環境変数・シークレット
- **python-security.instructions.md** — セキュリティ・脆弱性防止
- **python-documentation.instructions.md** — ドキュメント生成・Sphinx
- **python-pyproject.instructions.md** — pyproject.toml・ツール構成

**データ処理:**
- **python-pandas.instructions.md** — pandas コード品質・基本イディオム
- **python-pandas-performance.instructions.md** — pandas パフォーマンス最適化・大規模データ処理
- **python-openpyxl.instructions.md** — openpyxl ベストプラクティス・Excel 操作

**Django:**
- **django.instructions.md** — モデル設計・クエリ最適化・ビュー・Signals
- **django-api.instructions.md** — DRF シリアライザー・認証・テスト
- **django-infra.instructions.md** — マイグレーション・API 設計
- **django-celery.instructions.md** — Celery タスク設計・リトライ・冪等性

### skills/（プロセス・手順）

開発プロセスの手順をオンデマンドで参照するためのスキル定義：

- **tdd** — テスト駆動開発（Red → Green → Refactor）
- **code-review** — PR レビューのチェックリストと手順
- **refactoring** — テストで保護してから段階的に変更
- **debugging** — 再現 → 仮説 → 検証のサイクル

## GitHub Actions

### ci.yml

PR およびmain ブランチへの push 時に自動実行：

1. **ruff check** — リント
2. **ruff format --check** — フォーマット確認
3. **pytest --cov** — テスト実行 + カバレッジ計測
4. **カバレッジレポート** — PR コメントに結果を投稿

### Copilot コードレビュー（ブランチルールセットで設定）

Copilot コードレビューは GitHub Actions ではなく、リポジトリのブランチルールセットで有効化する：

1. Settings → Rules → Rulesets → 「New branch ruleset」
2. 「Automatically request Copilot code review」にチェック

または GitHub CLI から手動リクエスト：

```bash
gh pr edit --add-reviewer @copilot
```

> **注意:** Copilot Pro 以上のプランが必要（プレミアムリクエストを消費）。

## 参考にしたスキル・リソース

### Claude Code / Copilot スキル

| スキル名 | リポジトリ | スター数 | 内容・参考にした点 |
|----------|-----------|---------|-------------------|
| `python-performance-optimization` | [wshobson/agents](https://github.com/wshobson/agents) | 32.8K | CPU/メモリプロファイリング、20+ 最適化パターン、NumPy ベクトル化。パフォーマンス指針に反映 |
| `python-testing-patterns` | [wshobson/agents](https://github.com/wshobson/agents) | 32.8K | pytest フィクスチャ・パラメータ化・プロパティベーステスト。テスト規約に反映 |
| `python-design-patterns` | [wshobson/agents](https://github.com/wshobson/agents) | 32.8K | KISS, SRP, コンポジション、Rule of Three。設計原則に反映 |
| `python-anti-patterns` | [wshobson/agents](https://github.com/wshobson/agents) | 32.8K | 14+ アンチパターン（散在リトライ、bare except、型安全性）。禁止事項に反映 |
| `python-error-handling` | [wshobson/agents](https://github.com/wshobson/agents) | 32.8K | Pydantic バリデーション、例外階層、バッチエラー追跡。エラーハンドリング規約に反映 |
| `python-resource-management` | [wshobson/agents](https://github.com/wshobson/agents) | 32.8K | コンテキストマネージャー、ExitStack、ストリーミング。リソース管理規約に反映 |
| `modern-python` | [trailofbits/modern-python-skills](https://github.com/trailofbits/modern-python-skills) | — | uv, ruff, ty 等のモダンツールチェーン。コードスタイル・ツール選定に反映 |
| `django-expert` | [jeffallan/django-expert](https://github.com/jeffallan/django-expert) | — | Django 5.0 + DRF モデル設計、ORM 最適化、JWT 認証。Django 規約に反映 |
| `python-patterns` | [affaan-m/everything-claude-code](https://github.com/AffaanM/everything-claude-code) | 131K | Protocol, dataclass, DI パターン。Python コード構成に反映 |
| `python-testing` | [affaan-m/everything-claude-code](https://github.com/AffaanM/everything-claude-code) | 131K | pytest ベストプラクティス、hypothesis。テスト規約に反映 |
| `backend-patterns` | [affaan-m/everything-claude-code](https://github.com/AffaanM/everything-claude-code) | 131K | Repository パターン、N+1 防止、キャッシュ戦略。バックエンド設計に反映 |
| `coding-standards` | [affaan-m/everything-claude-code](https://github.com/AffaanM/everything-claude-code) | 131K | コード品質原則（KISS, DRY, YAGNI）、コードスメル検出。共通ルールに反映 |
| `django-expert` | [vintasoftware/django-ai-plugins](https://github.com/vintasoftware/django-ai-plugins) | 37 | Django コンサルティング企業 Vinta Software による総合ガイド。Django 規約の実践的知見に反映 |
| `django-security` | [affaan-m/everything-claude-code](https://github.com/AffaanM/everything-claude-code) | 131K | HTTPS/HSTS, Argon2, RBAC, XSS/SQLi 防止。セキュリティ規約に反映 |
| `python-configuration` | [wshobson/agents](https://github.com/wshobson/agents) | 32.8K | pydantic-settings、環境変数管理、シークレット。設定管理規約に反映 |
| `django-celery-expert` | [vintasoftware/django-ai-plugins](https://github.com/vintasoftware/django-ai-plugins) | 37 | Celery タスク冪等性、リトライ戦略、Beat 設定。Celery 規約に反映 |

### Copilot Instructions 設計の参考

| リソース | 参考にした点 |
|----------|-------------|
| [GitHub Copilot Instructions 公式ドキュメント](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-instructions-for-github-copilot) | Instructions / Skills の構成、applyTo パターン |
| [GitHub Blog: Custom Instructions Tips](https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/) | 最適サイズ（2,000文字以内）、簡潔さの重要性 |
| [GitHub Copilot Code Review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review) | Code Review の 4,000文字制限 |
| [Claude Code Superpowers](https://github.com/jamiecurnow/superpowers) | TDD・デバッグ等のスキル設計の参考元 |

### ツール

- [ruff](https://docs.astral.sh/ruff/) — Python フォーマッター / リンター
- [uv](https://docs.astral.sh/uv/) — Python パッケージマネージャー
- [pytest](https://docs.pytest.org/) — テストフレームワーク
