# 共通コーディングガイドライン

## 言語規約
- コメント、docstring、説明文はすべて日本語で記述する
- 変数名・関数名・クラス名は英語（snake_case / PascalCase）で記述する

## TDD（テスト駆動開発）【最優先ルール】
**テストのない実装コードは受け入れない。** `.github/skills/tdd/SKILL.md` の手順を厳守する。

## コードスタイル
- ruff（フォーマッター / リンター）、uv（パッケージ管理）、pytest（テスト）
- 行の長さ: 120文字以内
- インポート順序: 標準ライブラリ → サードパーティ → ローカル
- すべての公開関数に型ヒントを付与する（`T | None` 構文を使用）

## docstring
- Google スタイルの docstring を使用する
- 公開 API と複雑な関数には Args, Returns, Raises, Example セクションを記述する
- 型情報は型ヒントで表現し、docstring 内での重複記述は避ける
- すべてのモジュールファイルの先頭にモジュールレベルの docstring を記述する

## エラーハンドリング
- 具体的な例外クラスを使用する。`except Exception: pass` は禁止
- 例外チェインには `raise ... from e` を使用する

## セキュリティ
- API キー・トークン・パスワードのハードコード禁止 → 環境変数で管理
- SQL はパラメータ化クエリまたは ORM を使用する

## Git 規約
- コミットメッセージ: `type(scope): description`（feat, fix, refactor, test, docs, chore, ci）
- ブランチ名: `type/short-description`

## ロギング
- `logging.getLogger(__name__)` を使用。`print()` 禁止
## プロセススキル（該当作業時に必ず参照）
- TDD: `.github/skills/tdd/SKILL.md`
- レビュー: `.github/skills/code-review/SKILL.md`
- リファクタリング: `.github/skills/refactoring/SKILL.md`
- デバッグ: `.github/skills/debugging/SKILL.md`
