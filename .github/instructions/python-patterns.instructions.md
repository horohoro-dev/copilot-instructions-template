---
applyTo: "**/*.py"
description: "Python テスト・パフォーマンス・アンチパターン"
---

# Python テスト・パフォーマンス

## テスト
- pytest を使用する
- AAA パターン（Arrange → Act → Assert）に従う
- `@pytest.mark.parametrize` でパラメータ化テストを記述する
- フィクスチャでセットアップを再利用する
- テスト命名: `test_<対象>_<条件>_<期待結果>`

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
```

## パフォーマンス

**原則: 計測してから最適化する。** プロファイリングなしに最適化を行わない。`cProfile`、`line_profiler`、`memory_profiler` 等で実際のボトルネックを特定してから改善する。

- リスト内包表記 > `for` ループ
- ジェネレータでメモリ効率を改善する
- 文字列結合には `str.join()` を使用する
- 辞書ルックアップ O(1) > リスト検索 O(n)

```python
# Bad
result = ""
for item in items:
    result += str(item)

# Good
result = "".join(str(item) for item in items)
```

## アンチパターン（禁止事項）
- ベアな `except Exception: pass`
- I/O とビジネスロジックの混在
- ORM モデルの直接公開（API レスポンスにそのまま返さない）
- ハードコードされた設定値（環境変数や設定ファイルを使う）
- 5階層以上のネスト（早期リターンやガード句で解消する）
