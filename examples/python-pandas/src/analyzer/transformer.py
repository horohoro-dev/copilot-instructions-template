"""データ変換・集計モジュール。

pandasのベクトル化演算、groupby、ピボットテーブルを活用して
データの変換と集計を行う。iterrows()は使用せず、
ベクトル化された操作のみを利用する。
"""

import pandas as pd

# サポートされている集計関数の一覧
_SUPPORTED_AGG_FUNCS = frozenset({"sum", "mean", "min", "max", "count", "std", "var"})


def aggregate_by_group(
    df: pd.DataFrame,
    group_col: str,
    agg_col: str,
    agg_func: str,
) -> pd.DataFrame:
    """指定列でグループ化し、集計関数を適用する。

    pandasの組み込みgroupby集計メソッドを使用し、
    apply()を避けてパフォーマンスを最大化する。

    Args:
        df: 入力DataFrame。
        group_col: グループ化に使用する列名。
        agg_col: 集計対象の列名。
        agg_func: 集計関数名（sum, mean, min, max, count, std, var）。

    Returns:
        グループ化・集計されたDataFrame。

    Raises:
        ValueError: サポートされていない集計関数を指定した場合。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "product": ["A", "A", "B"],
        ...     "quantity": [10, 20, 30],
        ... })
        >>> result = aggregate_by_group(df, "product", "quantity", "sum")
        >>> result[result["product"] == "A"]["quantity"].values[0]
        30
    """
    if agg_func not in _SUPPORTED_AGG_FUNCS:
        raise ValueError(
            f"サポートされていない集計関数: '{agg_func}'。"
            f"使用可能: {sorted(_SUPPORTED_AGG_FUNCS)}"
        )

    # 組み込みの集計メソッドを直接呼び出す（apply()より高速）
    result = df.groupby(group_col, as_index=False).agg({agg_col: agg_func})
    return result


def add_computed_column(
    df: pd.DataFrame,
    new_col: str,
    col_a: str,
    col_b: str,
    operation: str,
) -> pd.DataFrame:
    """2つの列からベクトル化演算で新しい列を追加する。

    元のDataFrameは変更せず、新しいDataFrameを返す。
    すべての演算はpandasのベクトル化演算を使用する。

    Args:
        df: 入力DataFrame。
        new_col: 新しく追加する列名。
        col_a: 演算の左辺となる列名。
        col_b: 演算の右辺となる列名。
        operation: 演算の種類（add, subtract, multiply, divide）。

    Returns:
        計算列が追加された新しいDataFrame。

    Raises:
        ValueError: サポートされていない演算を指定した場合。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"qty": [10, 20], "price": [100, 200]})
        >>> result = add_computed_column(df, "revenue", "qty", "price", "multiply")
        >>> result["revenue"].tolist()
        [1000, 4000]
    """
    # ベクトル化演算のマッピング
    operations = {
        "add": lambda a, b: a + b,
        "subtract": lambda a, b: a - b,
        "multiply": lambda a, b: a * b,
        "divide": lambda a, b: a / b,
    }

    if operation not in operations:
        raise ValueError(
            f"サポートされていない演算: '{operation}'。"
            f"使用可能: {sorted(operations.keys())}"
        )

    # 元のDataFrameを変更しないようコピーする
    result = df.copy()
    result[new_col] = operations[operation](result[col_a], result[col_b])
    return result


def create_pivot_table(
    df: pd.DataFrame,
    index_col: str,
    columns_col: str,
    values_col: str,
    agg_func: str = "sum",
) -> pd.DataFrame:
    """ピボットテーブルを作成する。

    pandasの組み込みpivot_table関数を使用して、
    行・列・値を指定したクロス集計テーブルを生成する。

    Args:
        df: 入力DataFrame。
        index_col: ピボットテーブルの行となる列名。
        columns_col: ピボットテーブルの列となる列名。
        values_col: 集計対象の値の列名。
        agg_func: 集計関数名。

    Returns:
        ピボットテーブルのDataFrame。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "date": ["2024-01", "2024-01", "2024-02"],
        ...     "product": ["A", "B", "A"],
        ...     "qty": [10, 20, 30],
        ... })
        >>> pivot = create_pivot_table(df, "date", "product", "qty")
    """
    result = pd.pivot_table(
        df,
        index=index_col,
        columns=columns_col,
        values=values_col,
        aggfunc=agg_func,
    )
    # MultiIndex列をフラット化
    if hasattr(result.columns, "droplevel"):
        try:
            result.columns = result.columns.droplevel(0)
        except (ValueError, IndexError):
            pass
    result.columns.name = None
    return result
