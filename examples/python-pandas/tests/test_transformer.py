"""transformer モジュールのテスト。

データ変換・集計機能を検証する。
"""

import pandas as pd
import pytest

from analyzer.transformer import (
    add_computed_column,
    aggregate_by_group,
    create_pivot_table,
)


class TestAggregateByGroup:
    """aggregate_by_group 関数のテスト。"""

    def test_単一列でグループ集計(self, sample_sales_df: pd.DataFrame) -> None:
        """product列でグループ化し合計を算出する。"""
        result = aggregate_by_group(
            sample_sales_df, group_col="product", agg_col="quantity", agg_func="sum"
        )
        assert isinstance(result, pd.DataFrame)
        # A: 10+15+30=55, B: 20+25=45
        a_row = result[result["product"] == "A"]
        assert a_row["quantity"].values[0] == 55
        b_row = result[result["product"] == "B"]
        assert b_row["quantity"].values[0] == 45

    def test_平均値で集計(self, sample_sales_df: pd.DataFrame) -> None:
        """平均値での集計が正しく動作する。"""
        result = aggregate_by_group(
            sample_sales_df, group_col="product", agg_col="price", agg_func="mean"
        )
        a_row = result[result["product"] == "A"]
        assert a_row["price"].values[0] == pytest.approx(100.0)

    @pytest.mark.parametrize(
        "agg_func,expected_a",
        [
            ("sum", 55),
            ("mean", 55 / 3),
            ("min", 10),
            ("max", 30),
            ("count", 3),
        ],
    )
    def test_各種集計関数(
        self,
        sample_sales_df: pd.DataFrame,
        agg_func: str,
        expected_a: float,
    ) -> None:
        """各種集計関数が正しく動作する。"""
        result = aggregate_by_group(
            sample_sales_df,
            group_col="product",
            agg_col="quantity",
            agg_func=agg_func,
        )
        a_row = result[result["product"] == "A"]
        assert a_row["quantity"].values[0] == pytest.approx(expected_a)

    def test_不正な集計関数でValueError(self, sample_sales_df: pd.DataFrame) -> None:
        """サポートされていない集計関数を指定するとValueErrorが発生する。"""
        with pytest.raises(ValueError, match="サポートされていない集計関数"):
            aggregate_by_group(
                sample_sales_df,
                group_col="product",
                agg_col="quantity",
                agg_func="median_absolute_deviation",
            )


class TestAddComputedColumn:
    """add_computed_column 関数のテスト。"""

    def test_乗算で計算列を追加(self, sample_sales_df: pd.DataFrame) -> None:
        """quantity * price で売上額の列を追加する。"""
        result = add_computed_column(
            sample_sales_df,
            new_col="revenue",
            col_a="quantity",
            col_b="price",
            operation="multiply",
        )
        assert "revenue" in result.columns
        # 最初の行: 10 * 100 = 1000
        assert result["revenue"].iloc[0] == pytest.approx(1000.0)

    @pytest.mark.parametrize(
        "operation,expected_first",
        [
            ("add", 110.0),  # 10 + 100
            ("subtract", -90.0),  # 10 - 100
            ("multiply", 1000.0),  # 10 * 100
            ("divide", 0.1),  # 10 / 100
        ],
    )
    def test_各種演算(
        self,
        sample_sales_df: pd.DataFrame,
        operation: str,
        expected_first: float,
    ) -> None:
        """各種演算で計算列が正しく追加される。"""
        result = add_computed_column(
            sample_sales_df,
            new_col="result",
            col_a="quantity",
            col_b="price",
            operation=operation,
        )
        assert result["result"].iloc[0] == pytest.approx(expected_first)

    def test_元のDataFrameが変更されない(self, sample_sales_df: pd.DataFrame) -> None:
        """元のDataFrameは変更されず新しいDataFrameが返される。"""
        original_cols = list(sample_sales_df.columns)
        add_computed_column(
            sample_sales_df,
            new_col="revenue",
            col_a="quantity",
            col_b="price",
            operation="multiply",
        )
        assert list(sample_sales_df.columns) == original_cols


class TestCreatePivotTable:
    """create_pivot_table 関数のテスト。"""

    def test_ピボットテーブルを作成(self, sample_sales_df: pd.DataFrame) -> None:
        """日付×商品のピボットテーブルを作成する。"""
        result = create_pivot_table(
            sample_sales_df,
            index_col="date",
            columns_col="product",
            values_col="quantity",
            agg_func="sum",
        )
        assert isinstance(result, pd.DataFrame)
        assert "A" in result.columns
        assert "B" in result.columns

    def test_ピボットテーブルの値が正しい(self, sample_sales_df: pd.DataFrame) -> None:
        """ピボットテーブルの集計値が正しい。"""
        result = create_pivot_table(
            sample_sales_df,
            index_col="date",
            columns_col="product",
            values_col="quantity",
            agg_func="sum",
        )
        # 2024-01-01のA: 10
        row = result.loc[pd.Timestamp("2024-01-01")]
        assert row["A"] == 10
        assert row["B"] == 20
