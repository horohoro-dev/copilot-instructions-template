---
applyTo: "**/*.py"
description: "Python テスト・パフォーマンス・アンチパターン"
---

# Python テスト・パフォーマンス・アンチパターン

## テスト

- pytest を使用する
- AAA パターン（Arrange → Act → Assert）に従う
- `@pytest.mark.parametrize` でパラメータ化テストを記述する
- フィクスチャでセットアップを再利用する（`conftest.py` に共通定義）
- テスト命名: `test_<対象>_<条件>_<期待結果>`
- テスト構成: `tests/unit/`, `tests/integration/` に分離
- エッジケースと異常系を必ずテストする
- モックは外部依存のみ。過度なモックで偽の安心感を得ない

```python
@pytest.mark.parametrize("age,expected", [
    (17, False),
    (18, True),
    (65, True),
])
def test_is_adult_年齢に応じて正しい結果を返す(age: int, expected: bool) -> None:
    # Arrange
    user = User(age=age)
    # Act
    result = user.is_adult()
    # Assert
    assert result == expected

# 異常系テスト
def test_create_user_無効なメール_ValueErrorを送出():
    with pytest.raises(ValueError, match="無効なメール"):
        create_user(email="invalid")
```

## パフォーマンス

**原則: 計測してから最適化する。** `cProfile`、`line_profiler`、`memory_profiler` で実際のボトルネックを特定してから改善する。

| パターン | 速度 |
|---------|------|
| リスト内包表記 | > `for` ループ + `append` |
| `str.join()` | > `+=` 文字列結合（O(n) vs O(n²)） |
| `dict` / `set` ルックアップ O(1) | > `list` 検索 O(n) |
| ジェネレータ式 | メモリ O(1)、リストは O(n) |
| ローカル変数参照 | > グローバル変数参照 |
| 組み込み関数（`sum`, `map`） | > 手書きループ（C 実装） |
| `functools.lru_cache` | 繰り返し計算のキャッシュ |

## アンチパターン（禁止事項）

| 禁止 | 対策 |
|------|------|
| `except Exception: pass` | 具体的な例外クラスをキャッチし、ログ出力 |
| I/O とビジネスロジックの混在 | Repository パターンで分離 |
| ORM モデルの直接公開 | DTO / レスポンススキーマを使用 |
| ハードコードされた設定値 | 環境変数 + `pydantic-settings` |
| 5階層以上のネスト | 早期リターン / ガード句で解消 |
| タイムアウト/リトライの散在 | デコレータで一元化（`tenacity` 等） |
| 二重リトライ（アプリ + インフラ） | 1レイヤーのみでリトライ |
| 入力バリデーション漏れ | API 境界で即座にバリデーション |
| async 内でブロッキング呼び出し | async ネイティブライブラリを使用 |
| ハッピーパスのみのテスト | エラー・エッジケースも必ずテスト |
