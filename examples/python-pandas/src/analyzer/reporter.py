"""レポート出力モジュール。

DataFrameの集計結果をサマリーレポートとして出力する。
辞書形式およびフォーマット済みテキスト形式に対応する。
"""

import pandas as pd


def generate_summary(df: pd.DataFrame) -> dict:
    """DataFrameのサマリー情報を辞書形式で返す。

    行数、列数、列一覧、数値列の基本統計量、欠損値情報を含む
    サマリー辞書を生成する。数値統計にはpandasの組み込み
    ベクトル化メソッド（mean(), min(), max()等）を使用する。

    Args:
        df: サマリー対象のDataFrame。

    Returns:
        サマリー情報を含む辞書。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> summary = generate_summary(df)
        >>> summary["row_count"]
        3
    """
    summary: dict = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
    }

    # 数値列の基本統計量（ベクトル化メソッドを使用）
    numeric_cols = df.select_dtypes(include="number").columns
    numeric_summary: dict[str, dict] = {}
    for col in numeric_cols:
        numeric_summary[col] = {
            "mean": float(df[col].mean()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "std": float(df[col].std()),
            "sum": float(df[col].sum()),
        }
    summary["numeric_summary"] = numeric_summary

    # 欠損値情報（ベクトル化されたisnull().sum()を使用）
    missing = df.isnull().sum()
    missing_dict = {col: int(missing[col]) for col in df.columns if missing[col] > 0}
    summary["missing_values"] = missing_dict

    return summary


def generate_summary_text(df: pd.DataFrame) -> str:
    """DataFrameのサマリー情報をフォーマット済みテキストで返す。

    人間が読みやすい形式でサマリーレポートを生成する。

    Args:
        df: サマリー対象のDataFrame。

    Returns:
        フォーマット済みサマリーテキスト。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"x": [1, 2, 3]})
        >>> text = generate_summary_text(df)
        >>> "行数" in text
        True
    """
    summary = generate_summary(df)
    lines: list[str] = []

    lines.append("=" * 50)
    lines.append("データサマリーレポート")
    lines.append("=" * 50)
    lines.append(f"行数: {summary['row_count']}")
    lines.append(f"列数: {summary['column_count']}")
    lines.append(f"列一覧: {', '.join(summary['columns'])}")
    lines.append("")

    # 数値列の統計情報
    if summary["numeric_summary"]:
        lines.append("--- 数値列の統計情報 ---")
        for col, stats in summary["numeric_summary"].items():
            lines.append(f"  {col}:")
            lines.append(f"    平均: {stats['mean']:.4f}")
            lines.append(f"    最小: {stats['min']:.4f}")
            lines.append(f"    最大: {stats['max']:.4f}")
            lines.append(f"    標準偏差: {stats['std']:.4f}")
            lines.append(f"    合計: {stats['sum']:.4f}")
        lines.append("")

    # 欠損値情報
    if summary["missing_values"]:
        lines.append("--- 欠損値情報 ---")
        for col, count in summary["missing_values"].items():
            lines.append(f"  {col}: {count} 件")
    else:
        lines.append("欠損値: なし")

    lines.append("=" * 50)

    return "\n".join(lines)
