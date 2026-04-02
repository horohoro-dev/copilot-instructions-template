---
applyTo: "**/*.py,**/*.rst,**/*.md,**/conf.py"
description: "Python ドキュメント生成・Sphinx・API ドキュメント"
---

# Python ドキュメント規約

## docstring スタイル

Google スタイルを標準とする。型情報は型ヒントで表現し、docstring 内で重複しない。

```python
def calculate_discount(
    order_total: float,
    coupon_code: str | None = None,
) -> float:
    """注文合計に対する割引額を計算する。

    Args:
        order_total: 注文合計金額（税抜）。
        coupon_code: クーポンコード。None の場合は割引なし。

    Returns:
        割引額。割引がない場合は 0.0。

    Raises:
        ValueError: order_total が負の場合。

    Example:
        >>> calculate_discount(10000, "SAVE10")
        1000.0
    """
```

## docstring の記述基準

| 対象 | 必須/任意 | セクション |
|------|----------|-----------|
| 公開モジュール | 必須 | 先頭にモジュールレベル docstring |
| 公開クラス | 必須 | クラスの目的、Attributes |
| 公開関数/メソッド | 必須 | Args, Returns, Raises |
| 内部関数（`_` prefix） | 任意 | 複雑な場合のみ |
| 自明な関数（getter 等） | 不要 | 名前で意図が明確 |

## Sphinx によるドキュメント生成

### プロジェクト構成

```
docs/
├── conf.py          # Sphinx 設定
├── index.rst        # トップページ
├── api/             # API リファレンス（autodoc）
├── guides/          # ユーザーガイド
└── _build/          # ビルド出力（Git 除外）
```

### conf.py 設定

```python
extensions = [
    "sphinx.ext.autodoc",       # docstring から API ドキュメント生成
    "sphinx.ext.napoleon",      # Google/NumPy スタイル docstring 対応
    "sphinx.ext.viewcode",      # ソースコードリンク
    "sphinx.ext.intersphinx",   # 外部ドキュメントへのリンク
    "myst_parser",              # Markdown 対応
]

# Napoleon 設定（Google スタイル）
napoleon_google_docstring = True
napoleon_numpy_docstring = False
```

### ビルドコマンド

```bash
# HTML ドキュメント生成
uv run sphinx-build -b html docs/ docs/_build/html

# docstring カバレッジ確認
uv run sphinx-build -b coverage docs/ docs/_build/coverage
```

## API ドキュメント自動生成

```bash
# autodoc 用の .rst ファイルを自動生成
uv run sphinx-apidoc -o docs/api/ src/mypackage/
```

## アンチパターン

| 禁止 | 代替 |
|------|------|
| 型情報を docstring に重複記述 | 型ヒントに任せる |
| `# コメント` でドキュメント代用 | docstring を使用 |
| 古い docstring を放置 | コード変更時に docstring も更新 |
| 全関数に docstring 強制 | 自明な関数（`__str__` 等）は不要 |
| `docs/_build/` を Git にコミット | `.gitignore` に追加 |
