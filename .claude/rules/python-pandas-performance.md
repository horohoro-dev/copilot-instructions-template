---
globs: "**/*.py"
description: "pandas パフォーマンス最適化・大規模データ処理"
---

# pandas パフォーマンス最適化

## Copy-on-Write（pandas 2.0+ / 3.0 でデフォルト）

```python
# pandas 2.x では明示的に有効化（3.0 では不要）
pd.options.mode.copy_on_write = True

# CoW 有効時: スライスは遅延コピー（書き込み時のみ実体化）
subset = df[["col_a", "col_b"]]   # ゼロコピー（ビュー）
subset["col_a"] = 0               # ここで初めてコピー発生

# CoW の恩恵: drop/rename/reset_index 等が高速化
df = df.drop(columns=["tmp"]).rename(columns={"old": "new"})  # 各ステップがビュー

# 注意: .to_numpy() は読み取り専用配列を返す → 書き込みには .copy()
arr = df["col"].to_numpy().copy()
```

## メモリ最適化

```python
# 読み込み時に dtype を絞る
df = pd.read_csv("large.csv", dtype={
    "id": "int32",           # int64 → int32 で半減
    "name": "category",      # 繰り返し文字列は category 型
    "amount": "float32",     # float64 → float32 で半減
})

# PyArrow バックエンド（メモリ効率・高速）
df = pd.read_csv("large.csv", dtype_backend="pyarrow")
df = pd.read_parquet("data.parquet", dtype_backend="pyarrow")

# 不要列は読み込まない
df = pd.read_csv("large.csv", usecols=["id", "name", "amount"])
```

## チャンク処理（メモリ不足時）

```python
chunks = pd.read_csv("huge.csv", chunksize=50_000)
results = []
for chunk in chunks:
    processed = chunk.groupby("category")["amount"].sum()
    results.append(processed)
final = pd.concat(results).groupby(level=0).sum()
```

## 大規模 groupby / merge

```python
# groupby: 組み込み集約を使う（apply より高速）
df.groupby("category").agg(
    total=("amount", "sum"),
    count=("id", "count"),
    avg=("amount", "mean"),
)

# merge: 不要な列は事前に削除してメモリ節約
df2_slim = df2[["key", "needed_col"]]
merged = df1.merge(df2_slim, on="key")
```

## 並列処理の判断基準

| データ規模 | 推奨アプローチ |
|-----------|--------------|
| 〜数万行 | pandas 単体で十分 |
| 数万〜数十万行 | dtype 最適化 + チャンク処理 |
| 百万行超 | `polars`（Rust 製）を検討 |
| CPU バウンド集計 | `multiprocessing.Pool` + チャンク分割 |
| I/O バウンド（複数ファイル） | `concurrent.futures.ThreadPoolExecutor` |

## アンチパターン

| 禁止 | 代替 |
|------|------|
| `iterrows()` | ベクトル化演算 |
| `df.append()` ループ | `pd.concat([list])` 一括 |
| `df.copy()` の多用 | CoW に任せる / 必要な場面のみ |
| `apply(lambda)` で単純演算 | ベクトル化演算 |
| Parquet を CSV で代用 | 列指向の Parquet を使う |
