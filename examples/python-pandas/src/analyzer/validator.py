"""データ検証モジュール。

DataFrameのデータ整合性チェックを行う。
欠損値の検出、型の検証、値の範囲チェックに対応する。
"""

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ValidationResult:
    """検証結果を格納するデータクラス。

    Attributes:
        is_valid: 検証が成功したかどうか。
        errors: 検出されたエラーメッセージのリスト。
        missing_counts: 列ごとの欠損値数。
        out_of_range_count: 範囲外の値の数。
    """

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    missing_counts: dict[str, int] = field(default_factory=dict)
    out_of_range_count: int = 0


def check_missing_values(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> ValidationResult:
    """DataFrameの欠損値をチェックする。

    指定された列（省略時は全列）の欠損値数を集計し、
    欠損値がある場合はis_valid=Falseを返す。

    Args:
        df: 検査対象のDataFrame。
        columns: 検査対象の列名リスト。省略時は全列。

    Returns:
        欠損値の検証結果。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1, None, 3], "b": [4, 5, 6]})
        >>> result = check_missing_values(df)
        >>> result.is_valid
        False
        >>> result.missing_counts["a"]
        1
    """
    target_cols = columns if columns is not None else list(df.columns)
    # ベクトル化されたisnull().sum()を使用
    missing = df[target_cols].isnull().sum()

    result = ValidationResult()
    result.missing_counts = {col: int(missing[col]) for col in target_cols}

    if missing.sum() > 0:
        result.is_valid = False
        for col in target_cols:
            count = int(missing[col])
            if count > 0:
                result.errors.append(f"列 '{col}' に {count} 件の欠損値があります")

    return result


def check_types(
    df: pd.DataFrame,
    expected_types: dict[str, str],
) -> ValidationResult:
    """DataFrameの列の型が期待通りか検証する。

    Args:
        df: 検査対象のDataFrame。
        expected_types: 列名をキー、期待するdtype文字列を値とする辞書。

    Returns:
        型検証の結果。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"x": [1, 2], "y": [1.0, 2.0]})
        >>> result = check_types(df, {"x": "int64", "y": "float64"})
        >>> result.is_valid
        True
    """
    result = ValidationResult()

    for col, expected_dtype in expected_types.items():
        if col not in df.columns:
            result.is_valid = False
            result.errors.append(f"列 '{col}' がDataFrameに存在しません")
            continue

        actual_dtype = str(df[col].dtype)
        if actual_dtype != expected_dtype:
            result.is_valid = False
            result.errors.append(
                f"列 '{col}' の型が不一致: 期待={expected_dtype}, 実際={actual_dtype}"
            )

    return result


def check_range(
    df: pd.DataFrame,
    column: str,
    min_val: float | int | None = None,
    max_val: float | int | None = None,
) -> ValidationResult:
    """指定列の値が範囲内に収まっているか検証する。

    ベクトル化された比較演算を使用して範囲チェックを行う。

    Args:
        df: 検査対象のDataFrame。
        column: 検査対象の列名。
        min_val: 最小値（指定時、この値以上であること）。
        max_val: 最大値（指定時、この値以下であること）。

    Returns:
        範囲検証の結果。

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"score": [50, 75, 100]})
        >>> result = check_range(df, "score", min_val=0, max_val=100)
        >>> result.is_valid
        True
    """
    result = ValidationResult()
    series = df[column]

    # ベクトル化された比較演算
    out_of_range = pd.Series([False] * len(series), index=series.index)

    if min_val is not None:
        out_of_range = out_of_range | (series < min_val)

    if max_val is not None:
        out_of_range = out_of_range | (series > max_val)

    count = int(out_of_range.sum())
    result.out_of_range_count = count

    if count > 0:
        result.is_valid = False
        result.errors.append(
            f"列 '{column}' に {count} 件の範囲外の値があります"
            f"（範囲: {min_val} - {max_val}）"
        )

    return result
