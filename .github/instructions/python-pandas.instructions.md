---
applyTo: "**/*.py"
description: "pandas ベストプラクティス"
---

# pandas ベストプラクティス

## 基本方針
- ベクトル化演算を優先する
- `iterrows()` 禁止 → `apply()` またはベクトル化演算を使用する
- 組み込みメソッド（`sum()`, `mean()`, `groupby()` 等）を活用する
- 大規模データはチャンク読み込みを検討する
- 適切な `dtype` を指定してメモリ効率を確保する

```python
# Bad: iterrows()
for _, row in df.iterrows():
    row["total"] = row["price"] * row["quantity"]

# Good: ベクトル化演算
df["total"] = df["price"] * df["quantity"]
```
