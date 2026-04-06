---
globs: "**/*.py"
description: "pandas コード品質・基本イディオム"
---

# pandas 基本イディオム

## 選択・代入

```python
# Bad: チェイン代入（サイレントにコピーを変更、バグの原因）
df["col"][mask] = value

# Good: .loc で明示的に選択・代入
df.loc[mask, "col"] = value

# Good: 位置ベースは .iloc
first_row = df.iloc[0]
```

## メソッドチェイン（推奨スタイル）

```python
# Good: 1行1操作、括弧で囲む
result = (
    df
    .query("age >= 18")
    .assign(
        full_name=lambda d: d["first"] + " " + d["last"],
        is_senior=lambda d: d["age"] >= 65,
    )
    .groupby("department")
    .agg(count=("id", "count"), avg_age=("age", "mean"))
    .sort_values("count", ascending=False)
)

# .pipe() でカスタム関数をチェインに組み込む
def remove_outliers(df, col, n_std=3):
    mean, std = df[col].mean(), df[col].std()
    return df[df[col].between(mean - n_std * std, mean + n_std * std)]

result = df.pipe(remove_outliers, "price").assign(log_price=lambda d: np.log(d["price"]))
```

- チェインは7-8操作を目安に分割
- `inplace=True` は非推奨。代入式 `df = df.method()` を使う

## 演算の優先順位（速い順）

1. ベクトル化演算（NumPy / pandas 組み込み）
2. `groupby()` + 組み込み集約関数
3. `apply()` with `engine="numba"`（数値演算のみ）
4. `apply()`（最終手段）
5. `itertuples()`（行アクセスが不可避な場合）
6. **`iterrows()` は禁止**（型変換コスト大、常に最遅）

```python
# Bad
for _, row in df.iterrows():
    row["total"] = row["price"] * row["quantity"]

# Good: ベクトル化
df["total"] = df["price"] * df["quantity"]

# Good: 条件付き代入
df["category"] = np.where(df["price"] > 1000, "high", "normal")

# Good: 複数条件（pandas 2.2+）
df["tier"] = df["score"].case_when(
    caselist=[(df["score"] >= 90, "A"), (df["score"] >= 70, "B")],
    default="C",
)
```

## dtype の明示

```python
# 読み込み時に dtype を指定する（推奨）
df = pd.read_csv("data.csv", dtype={
    "id": "int32",
    "name": "string",         # object ではなく string を使う
    "category": "category",   # 繰り返し文字列
    "is_active": "boolean",   # nullable bool
    "count": "Int32",         # nullable integer（欠損値がある整数列）
})
```

## よくある間違い

| 間違い | 正しい方法 |
|--------|-----------|
| `df["col"][mask] = val` | `df.loc[mask, "col"] = val` |
| `df.append()` ループ | `pd.concat([list])` 一括 |
| `apply(lambda x: x*2)` 単純演算 | `df["col"] * 2` ベクトル化 |
| dtype 未指定の `read_csv` | `dtype=` で明示 |
| 文字列列を `object` 型のまま | `dtype="string"` を指定 |
| 欠損ありの整数を float に | `Int32` 等の nullable integer |
| `to_csv()` で `index=False` 忘れ | `df.to_csv("out.csv", index=False)` |

## テスト

```python
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

# Good: pandas 専用のアサーション（NaN 比較・列ごとの差分表示）
assert_frame_equal(result, expected)
assert_series_equal(result["col"], expected_series)

# pytest.fixture で小さなテスト用 DataFrame を定義
# I/O のテストは io.StringIO を使いファイル不要にする
```
