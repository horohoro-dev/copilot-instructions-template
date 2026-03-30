# 共通コーディングガイドライン

## 言語規約
- コメント、docstring、説明文はすべて日本語で記述する
- 変数名・関数名・クラス名は英語（snake_case / PascalCase）で記述する

## TDD（テスト駆動開発）方針【最優先ルール】

**実装コードを書く際は、`.github/skills/tdd/SKILL.md` の手順を厳守すること。** テストのない実装コードは受け入れない。

## コードスタイル
- フォーマッター / リンター: ruff（デフォルト設定に準拠）
- パッケージ管理: uv
- テストフレームワーク: pytest
- 行の長さ: 120文字以内
- インポート順序: 標準ライブラリ → サードパーティ → ローカル（ruff の isort 設定に準拠）

## 型ヒント
- すべての公開関数・メソッドに型ヒントを付与する
- `Optional[T]` ではなく `T | None` 構文を使用する（Python 3.10+）
- ジェネリクスとプロトコルを活用して型安全性を確保する

## docstring
- Google スタイルの docstring を使用する
- 公開 API と複雑な関数には Args, Returns, Raises, Example セクションを記述する
- 型情報は型ヒントで表現し、docstring 内での重複記述は避ける
- すべてのモジュールファイルの先頭にモジュールレベルの docstring を記述する

## 関数設計
- 1関数は50行以内を目安とする
- 単一責任の原則を守る
- ネストは3階層以内に抑え、早期リターンを活用する

## エラーハンドリング
- 外部入力のバリデーションは API 境界で行う
- 具体的な例外クラスを使用する（`ValueError`, `TypeError` 等）
- 例外チェインには `raise ... from e` を使用する
- ベアな `except Exception: pass` は禁止

## Git 規約
- コミットメッセージ: `type(scope): description` 形式（例: `feat(auth): ログイン機能を追加`）
- type: feat, fix, refactor, test, docs, chore, ci
- ブランチ名: `type/short-description`（例: `feat/user-auth`）

## セキュリティ
- API キー、トークン、パスワードをハードコードしない
- すべての秘密情報は環境変数で管理する
- `.env` ファイルはコミットしない
- ユーザー入力は必ずバリデーションする
- SQL はパラメータ化クエリまたは ORM を使用する

## 設計原則
- KISS（最もシンプルな解決策を選ぶ）
- 継承よりコンポジション
- 3回繰り返すまで抽象化しない（Rule of Three）
- 依存性注入でテスタビリティを確保する
- 関心の分離: API層 → サービス層 → リポジトリ層

## プロセススキル（必須参照）

以下のスキルは該当する作業時に必ず参照し、手順を厳守すること。

- **コードレビュー**: PR のレビュー時は `.github/skills/code-review/SKILL.md` に従う
- **リファクタリング**: コード改善時は `.github/skills/refactoring/SKILL.md` に従う
- **デバッグ**: バグ修正時は `.github/skills/debugging/SKILL.md` に従う
