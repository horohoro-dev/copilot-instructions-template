"""テスト共通フィクスチャ定義。

テスト全体で共有するサンプルDataFrameや一時CSVファイルを提供する。
"""

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_sales_df() -> pd.DataFrame:
    """売上データのサンプルDataFrameを返す。"""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"]
            ),
            "product": ["A", "B", "A", "B", "A"],
            "quantity": [10, 20, 15, 25, 30],
            "price": [100.0, 200.0, 100.0, 200.0, 100.0],
        }
    )


@pytest.fixture
def sample_csv_path(tmp_path: Path, sample_sales_df: pd.DataFrame) -> Path:
    """サンプル売上CSVファイルのパスを返す。"""
    csv_path = tmp_path / "sales.csv"
    sample_sales_df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_csv_with_missing(tmp_path: Path) -> Path:
    """欠損値を含むCSVファイルのパスを返す。"""
    df = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie", "Diana"],
            "age": [25, 30, None, 40],
            "score": [85.0, 90.0, 78.0, None],
        }
    )
    csv_path = tmp_path / "missing.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def large_sample_csv(tmp_path: Path) -> Path:
    """大規模CSVファイル（1000行）のパスを返す。"""
    import numpy as np

    rng = np.random.default_rng(42)
    n = 1000
    df = pd.DataFrame(
        {
            "id": range(n),
            "category": rng.choice(["X", "Y", "Z"], size=n),
            "value": rng.uniform(0, 1000, size=n).round(2),
            "count": rng.integers(1, 100, size=n),
        }
    )
    csv_path = tmp_path / "large.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def df_with_missing() -> pd.DataFrame:
    """欠損値を含むDataFrameを返す。"""
    return pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie", "Diana"],
            "age": [25, 30, None, 40],
            "score": [85.0, 90.0, 78.0, None],
        }
    )


@pytest.fixture
def df_with_types() -> pd.DataFrame:
    """型検証用のDataFrameを返す。"""
    return pd.DataFrame(
        {
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
        }
    )
