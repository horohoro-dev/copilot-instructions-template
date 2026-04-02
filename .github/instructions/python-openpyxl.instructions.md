---
applyTo: "**/*.py"
description: "openpyxl ベストプラクティス・Excel 操作"
---

# openpyxl ベストプラクティス

## 基本パターン

```python
from openpyxl import load_workbook, Workbook
from openpyxl.styles import NamedStyle, Font, PatternFill, Alignment

# セルは 1-based（A1 = row=1, column=1）。0 ではないので注意
ws.cell(row=1, column=1).value = "Header"

# マジックナンバーは名前付き定数にする
PRODUCT_ID_COL = 1
PRODUCT_NAME_COL = 2
```

### スタイル（NamedStyle を使い回す）

```python
# Bad: セルごとにスタイルを個別設定（遅く、ファイル肥大化）
for row in ws.iter_rows():
    for cell in row:
        cell.font = Font(bold=True)

# Good: NamedStyle を定義して適用
header_style = NamedStyle(
    name="header",
    font=Font(bold=True, size=12),
    fill=PatternFill("solid", fgColor="DAEEF3"),
    alignment=Alignment(horizontal="center"),
)
wb.add_named_style(header_style)
for cell in ws[1]:
    cell.style = "header"
```

### 数式

```python
# 数式は常に英語の関数名で書く（Excel が自動でローカライズ）
ws["C2"] = '=SUM(A2:B2)'
ws["D2"] = '=COUNTIF(A:A, ">0")'

# 数式の計算結果を読む場合は data_only=True
# 注意: Excel で最後に保存したキャッシュ値を返す
wb = load_workbook("file.xlsx", data_only=True)
```

## モード選択

| モード | 用途 | メモリ |
|--------|------|--------|
| `load_workbook()` 通常 | 読み書き（〜1万行） | 高 |
| `load_workbook(read_only=True)` | 読み取り専用 | 低 |
| `Workbook(write_only=True)` | 新規書き込み専用 | 低 |

```python
from contextlib import closing

# 読み取り専用（必ず close する）
with closing(load_workbook("data.xlsx", read_only=True)) as wb:
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        process_row(row)

# 書き込み専用（save は1回のみ）
wb = Workbook(write_only=True)
ws = wb.create_sheet()
ws.append(["ID", "Name", "Amount"])
for record in dataset:
    ws.append([record.id, record.name, record.amount])
wb.save("output.xlsx")
```

## よくある落とし穴

| 落とし穴 | 対策 |
|---------|------|
| セルは 1-based なのに 0 を指定 | `row=1, column=1` が A1 |
| 画像・グラフが load→save で消える | openpyxl はラウンドトリップ非対応 |
| `read_only` モードで close 忘れ | `with closing(wb)` を使う |
| マージセルの値読み取り | 左上セルのみ値を持つ |
| 制御文字を含むデータの書き込み | `IllegalCharacterError` を事前にstrip |
| `.xls` を開こうとする | openpyxl は `.xlsx` 専用。`.xls` は `xlrd` |
| `write_only` で2回 save | 1回しか save できない |
| `copy_worksheet` で画像・グラフ | セル・スタイルのみコピーされる |

## テンプレート活用

```python
# テンプレートファイルを読み込んで名前付き範囲にデータ注入
wb = load_workbook("template.xlsx")
ws = wb.active
ws["B2"] = company_name
ws["B3"] = report_date
# 必ず別名で保存（テンプレートを上書きしない）
wb.save("output.xlsx")

# VBA マクロ付きテンプレート
wb = load_workbook("template.xltm", keep_vba=True)
wb.save("output.xlsm")
```

## ライブラリ選択ガイド

| 用途 | 推奨ライブラリ |
|------|--------------|
| 既存 .xlsx の読み書き | **openpyxl** |
| 新規 .xlsx + 高度な書式 | **xlsxwriter**（書き込み専用） |
| DataFrame の単純な Excel 出力 | **pandas** `to_excel()` |
| VBA マクロ付き .xlsm | **openpyxl** (`keep_vba=True`) |
| レガシー .xls の読み取り | **xlrd** |
| 超大規模読み取り（100万行超） | **polars** / **calamine** |
