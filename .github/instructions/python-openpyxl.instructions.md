---
applyTo: "**/*.py"
description: "openpyxl ベストプラクティス・大規模 Excel 処理"
---

# openpyxl ベストプラクティス

## モード選択（最重要）

| モード | 用途 | メモリ使用量 |
|--------|------|-------------|
| `load_workbook()` 通常 | 小〜中規模（〜1万行）の読み書き | 高（全体をメモリに展開） |
| `load_workbook(read_only=True)` | 大規模ファイルの読み取り専用 | 低（行単位ストリーミング） |
| `Workbook(write_only=True)` | 大規模ファイルの書き込み専用 | 低（行単位フラッシュ） |

## 大規模ファイルの読み取り（数万〜数十万行）

```python
from openpyxl import load_workbook

# 必ず read_only=True を使用する
wb = load_workbook("large.xlsx", read_only=True, data_only=True)
ws = wb.active

# ジェネレータで行を処理（メモリ効率的）
for row in ws.iter_rows(min_row=2, values_only=True):
    process_row(row)

# 使用後は必ず閉じる
wb.close()
```

### コンテキストマネージャ推奨

```python
from contextlib import closing

with closing(load_workbook("large.xlsx", read_only=True)) as wb:
    ws = wb.active
    data = [row for row in ws.iter_rows(min_row=2, values_only=True)]
```

## 大規模ファイルの書き込み

```python
from openpyxl import Workbook

wb = Workbook(write_only=True)
ws = wb.create_sheet()

# ヘッダー
ws.append(["ID", "名前", "金額"])

# 行単位で追加（メモリに蓄積しない）
for record in large_dataset:
    ws.append([record.id, record.name, record.amount])

wb.save("output.xlsx")
```

## pandas 連携

```python
import pandas as pd

# 大規模 Excel → pandas（openpyxl エンジン）
df = pd.read_excel(
    "large.xlsx",
    engine="openpyxl",
    dtype={"id": "int32", "category": "category"},
)

# pandas → Excel 書き出し
with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="データ")
```

## アンチパターン

| 禁止 | 代替 |
|------|------|
| `read_only` なしで大規模ファイルを開く | `load_workbook(read_only=True)` |
| `ws.cell(row, col)` でループアクセス | `ws.iter_rows(values_only=True)` |
| `wb.close()` 忘れ（read_only モード） | `with closing(wb)` またはtry/finally |
| 通常モードで数万行書き込み | `write_only=True` モード |
| セル単位でスタイル設定（大量行） | 書き込み後に範囲指定でスタイル適用 |
| `data_only=False` で数式入りファイルを読む | `data_only=True` で計算結果を取得 |

## 並列処理の指針

- **複数シート**: `concurrent.futures.ThreadPoolExecutor` で並列読み取り可能
- **複数ファイル**: ファイル単位で `ProcessPoolExecutor` が有効
- **単一大規模シート**: 並列化の恩恵は小さい。チャンク処理で対応
- openpyxl はスレッドセーフではない → ファイル/ワークブック単位で分離

## 代替ライブラリの検討

| ライブラリ | 適用場面 |
|-----------|---------|
| `openpyxl` | 既存 .xlsx の読み書き、セル書式操作 |
| `xlsxwriter` | 新規 .xlsx の高速書き込み（読み取り不可） |
| `polars` | 大規模 Excel の高速読み取り（Rust 製） |
| `calamine`（via polars） | 100万行超の Excel 読み取り |
