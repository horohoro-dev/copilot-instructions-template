---
applyTo: "**/*.py"
description: "pandas ベストプラクティス・大規模データ処理"
---

# pandas ベストプラクティス

## 演算の優先順位（速い順）

1. ベクトル化演算（NumPy / pandas 組み込み）
2. `groupby()` + 組み込み集約関数
3. `apply()` with `engine="numba"`（数値演算のみ）
4. `apply()`（最終手段）
5. `itertuples()`（行アクセスが必要な場合）
6. **`iterrows()` は禁止**（型変換コスト大、常に最遅）

```python
# Bad: iterrows()
for _, row in df.iterrows():
    row["total"] = row["price"] * row["quantity"]

# Good: ベクトル化演算
df["total"] = df["price"] * df["quantity"]

# Good: 条件付き代入
df["category"] = np.where(df["price"] > 1000, "高額", "通常")
```

## 大規模データ処理（数万〜数十万行）

### メモリ最適化（必須）

```python
# 読み込み時に dtype を明示する
df = pd.read_csv("large.csv", dtype={
    "id": "int32",           # int64 → int32 で半減
    "name": "category",      # 繰り返し文字列は category 型
    "amount": "float32",     # float64 → float32 で半減
    "flag": "bool",
})

# 既存 DataFrame の最適化
df["status"] = df["status"].astype("category")  # ユニーク値が少ない列
```

### チャンク読み込み（メモリ不足時）

```python
chunks = pd.read_csv("huge.csv", chunksize=50_000)
results = []
for chunk in chunks:
    processed = chunk.groupby("category")["amount"].sum()
    results.append(processed)
final = pd.concat(results).groupby(level=0).sum()
```

### 大規模 groupby / merge

```python
# groupby: 組み込み集約を使う（apply より高速）
df.groupby("category").agg(
    total=("amount", "sum"),
    count=("id", "count"),
    avg=("amount", "mean"),
)

# merge: キー列でソート済みなら高速
df1 = df1.sort_values("key")
df2 = df2.sort_values("key")
merged = pd.merge(df1, df2, on="key")

# 不要な列は merge 前に削除してメモリ節約
df2_slim = df2[["key", "needed_col"]]
merged = df1.merge(df2_slim, on="key")
```

## アンチパターン

| 禁止 | 代替 |
|------|------|
| `iterrows()` | ベクトル化演算 / `apply()` |
| `df.append()` in ループ | `pd.concat([list])` 一括結合 |
| `df.copy()` の多用 | 必要な場面のみコピー |
| `apply(lambda x: ...)` で単純演算 | ベクトル化演算 |
| dtype 未指定の `read_csv` | 明示的に dtype 指定 |
| `inplace=True` の多用 | 代入式 `df = df.method()` を推奨 |

## 並列処理の判断基準

- **数十万行以下**: pandas 単体で十分。チャンク処理で対応
- **百万行超**: `polars`（Rust 製、pandas 互換 API）を検討
- **CPU バウンド集計**: `multiprocessing.Pool` + チャンク分割
- **I/O バウンド（複数ファイル読み込み）**: `concurrent.futures.ThreadPoolExecutor`
- pandas の `apply()` は GIL 制約で並列化の恩恵が小さい
