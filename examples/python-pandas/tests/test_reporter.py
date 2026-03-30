"""reporter モジュールのテスト。

レポート出力機能を検証する。
"""

import pandas as pd
import pytest

from analyzer.reporter import generate_summary, generate_summary_text


class TestGenerateSummary:
    """generate_summary 関数のテスト。"""

    def test_基本統計情報を含む(self, sample_sales_df: pd.DataFrame) -> None:
        """サマリーに行数・列数・基本統計が含まれる。"""
        result = generate_summary(sample_sales_df)
        assert isinstance(result, dict)
        assert result["row_count"] == 5
        assert result["column_count"] == 4
        assert "columns" in result
        assert "numeric_summary" in result

    def test_数値列の統計情報(self, sample_sales_df: pd.DataFrame) -> None:
        """数値列の平均・最大・最小が正しく計算される。"""
        result = generate_summary(sample_sales_df)
        numeric = result["numeric_summary"]
        assert "quantity" in numeric
        assert numeric["quantity"]["mean"] == pytest.approx(20.0)
        assert numeric["quantity"]["min"] == 10
        assert numeric["quantity"]["max"] == 30

    def test_欠損値情報を含む(self, df_with_missing: pd.DataFrame) -> None:
        """欠損値の数がサマリーに含まれる。"""
        result = generate_summary(df_with_missing)
        assert "missing_values" in result
        assert result["missing_values"]["name"] == 1

    def test_列一覧が正しい(self, sample_sales_df: pd.DataFrame) -> None:
        """列名の一覧が正しく返される。"""
        result = generate_summary(sample_sales_df)
        assert result["columns"] == ["date", "product", "quantity", "price"]


class TestGenerateSummaryText:
    """generate_summary_text 関数のテスト。"""

    def test_テキスト形式で出力(self, sample_sales_df: pd.DataFrame) -> None:
        """フォーマットされた文字列が返される。"""
        result = generate_summary_text(sample_sales_df)
        assert isinstance(result, str)
        assert "行数" in result
        assert "列数" in result

    def test_数値統計が含まれる(self, sample_sales_df: pd.DataFrame) -> None:
        """数値列の統計情報がテキストに含まれる。"""
        result = generate_summary_text(sample_sales_df)
        assert "quantity" in result
        assert "price" in result

    def test_欠損値情報がテキストに含まれる(
        self, df_with_missing: pd.DataFrame
    ) -> None:
        """欠損値がある場合、その情報がテキストに含まれる。"""
        result = generate_summary_text(df_with_missing)
        assert "欠損値" in result
