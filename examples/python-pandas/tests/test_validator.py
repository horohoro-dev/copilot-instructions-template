"""validator モジュールのテスト。

データ検証機能を検証する。
"""

import pandas as pd
import pytest

from analyzer.validator import (
    ValidationResult,
    check_missing_values,
    check_range,
    check_types,
)


class TestCheckMissingValues:
    """check_missing_values 関数のテスト。"""

    def test_欠損値ありの検出(self, df_with_missing: pd.DataFrame) -> None:
        """欠損値を含むDataFrameで欠損情報が正しく返される。"""
        result = check_missing_values(df_with_missing)
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert result.missing_counts["name"] == 1
        assert result.missing_counts["age"] == 1
        assert result.missing_counts["score"] == 1

    def test_欠損値なしのDataFrame(self, sample_sales_df: pd.DataFrame) -> None:
        """欠損値を含まないDataFrameではis_valid=True。"""
        result = check_missing_values(sample_sales_df)
        assert result.is_valid
        assert all(v == 0 for v in result.missing_counts.values())

    def test_検査対象列の指定(self, df_with_missing: pd.DataFrame) -> None:
        """指定した列のみを検査対象にできる。"""
        result = check_missing_values(df_with_missing, columns=["name"])
        assert not result.is_valid
        assert "name" in result.missing_counts
        assert "age" not in result.missing_counts


class TestCheckTypes:
    """check_types 関数のテスト。"""

    def test_期待する型と一致(self, df_with_types: pd.DataFrame) -> None:
        """各列の型が期待通りであればis_valid=True。"""
        # pandas 3.0以降では文字列列のdtypeは"str"（StringDtype）
        str_dtype = str(df_with_types["str_col"].dtype)
        expected = {"int_col": "int64", "float_col": "float64", "str_col": str_dtype}
        result = check_types(df_with_types, expected_types=expected)
        assert result.is_valid

    def test_型の不一致を検出(self, df_with_types: pd.DataFrame) -> None:
        """型が一致しない列がある場合is_valid=False。"""
        expected = {"int_col": "float64", "str_col": "int64"}
        result = check_types(df_with_types, expected_types=expected)
        assert not result.is_valid
        assert len(result.errors) == 2

    def test_存在しない列名でエラー(self, df_with_types: pd.DataFrame) -> None:
        """DataFrameに存在しない列名を指定するとエラー情報に含まれる。"""
        expected = {"nonexistent": "int64"}
        result = check_types(df_with_types, expected_types=expected)
        assert not result.is_valid


class TestCheckRange:
    """check_range 関数のテスト。"""

    def test_範囲内のデータ(self, sample_sales_df: pd.DataFrame) -> None:
        """全データが範囲内であればis_valid=True。"""
        result = check_range(sample_sales_df, column="quantity", min_val=0, max_val=100)
        assert result.is_valid

    def test_範囲外のデータ検出(self, sample_sales_df: pd.DataFrame) -> None:
        """範囲外のデータがあればis_valid=False。"""
        result = check_range(sample_sales_df, column="quantity", min_val=15, max_val=25)
        assert not result.is_valid
        assert result.out_of_range_count > 0

    @pytest.mark.parametrize(
        "min_val,max_val,expected_valid",
        [
            (0, 100, True),
            (10, 30, True),
            (11, 30, False),  # 10が範囲外
            (10, 29, False),  # 30が範囲外
        ],
    )
    def test_境界値(
        self,
        sample_sales_df: pd.DataFrame,
        min_val: int,
        max_val: int,
        expected_valid: bool,
    ) -> None:
        """境界値が正しく検証される。"""
        result = check_range(
            sample_sales_df, column="quantity", min_val=min_val, max_val=max_val
        )
        assert result.is_valid == expected_valid

    def test_min_valのみ指定(self, sample_sales_df: pd.DataFrame) -> None:
        """最小値のみの指定で検証できる。"""
        result = check_range(sample_sales_df, column="quantity", min_val=0)
        assert result.is_valid

    def test_max_valのみ指定(self, sample_sales_df: pd.DataFrame) -> None:
        """最大値のみの指定で検証できる。"""
        result = check_range(sample_sales_df, column="quantity", max_val=100)
        assert result.is_valid
