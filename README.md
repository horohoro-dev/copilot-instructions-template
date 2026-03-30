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
│   ├── copilot-instructions.md           # 全体共通ルール
│   │
│   ├── instructions/                     # 言語・フレームワーク別ルール
│   │   ├── python.instructions.md        # applyTo: "**/*.py"
│   │   └── django.instructions.md        # applyTo: "**/views.py,**/models.py, ..."
│   │
│   ├── skills/                           # プロセス・手順の知識（オンデマンド）
│   │   ├── tdd/SKILL.md                  # テスト駆動開発の手順
│   │   ├── code-review/SKILL.md          # PR レビューの手順
│   │   ├── refactoring/SKILL.md          # リファクタリング手順
│   │   └── debugging/SKILL.md            # デバッグ手順
│   │
│   └── workflows/                        # GitHub Actions
│       └── ci.yml                        # ruff + pytest + カバレッジ
│
├── examples/                             # サンプルプロジェクト（実例）
│   ├── python-pandas/                    # Python + pandas による CSV データ分析
│   │   ├── pyproject.toml
│   │   ├── src/analyzer/                 # ソースコード
│   │   └── tests/                        # テストコード
│   │
│   └── django-app/                       # Django によるタスク管理 API
│       ├── pyproject.toml
│       ├── manage.py
│       ├── config/                       # Django 設定
│       ├── tasks/                        # タスク管理アプリ
│       └── tests/                        # テストコード
│
├── .claude/                              # 参考資料（Superpowers Skills 等）
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

### 3. 不要なファイルの削除

- `examples/` — サンプルプロジェクトは参考用。自プロジェクトには不要
- `.claude/` — Claude Code 参考資料。自プロジェクトには不要

## Copilot Instructions の構成

### copilot-instructions.md（全体共通）

すべてのファイルに適用される基本ルール：TDD 方針、コードスタイル、Git 規約、セキュリティ等。

### instructions/（言語・フレームワーク別）

`applyTo` で対象ファイルを指定し、言語・フレームワーク固有のルールを適用：

- **python.instructions.md** — pandas ベストプラクティス、型ヒント、インポート順序等
- **django.instructions.md** — モデル設計、クエリ最適化、セキュリティ等

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

## 参考

- [GitHub Copilot Instructions 公式ドキュメント](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-instructions-for-github-copilot)
- [GitHub Copilot Code Review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review)
- [Claude Code Superpowers プラグイン](https://github.com/jamiecurnow/superpowers) — TDD・デバッグ等のスキル設計の参考元
- [ruff](https://docs.astral.sh/ruff/) — Python フォーマッター / リンター
- [uv](https://docs.astral.sh/uv/) — Python パッケージマネージャー
- [pytest](https://docs.pytest.org/) — テストフレームワーク
