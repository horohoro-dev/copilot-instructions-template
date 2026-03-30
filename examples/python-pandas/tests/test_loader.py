"""loader モジュールのテスト。

CSVファイルの読み込み機能を検証する。
"""

from pathlib import Path

import pandas as pd
import pytest

from analyzer.loader import load_csv, load_csv_chunked


class TestLoadCsv:
    """load_csv 関数のテスト。"""

    def test_正常なCSVを読み込める(self, sample_csv_path: Path) -> None:
        """正常なCSVファイルを読み込み、DataFrameを返す。"""
        df = load_csv(sample_csv_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == ["date", "product", "quantity", "price"]

    def test_dtypeを指定して読み込める(self, sample_csv_path: Path) -> None:
        """dtype指定により適切な型でデータが読み込まれる。"""
        dtypes = {"quantity": "int32", "price": "float32"}
        df = load_csv(sample_csv_path, dtypes=dtypes)
        assert df["quantity"].dtype == "int32"
        assert df["price"].dtype == "float32"

    def test_存在しないファイルでFileNotFoundError(self, tmp_path: Path) -> None:
        """存在しないファイルパスを指定するとFileNotFoundErrorが発生する。"""
        with pytest.raises(FileNotFoundError, match="ファイルが見つかりません"):
            load_csv(tmp_path / "nonexistent.csv")

    def test_空のCSVでValueError(self, tmp_path: Path) -> None:
        """空のCSVファイルを読み込むとValueErrorが発生する。"""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")
        with pytest.raises(ValueError, match="空のファイル"):
            load_csv(empty_csv)

    def test_エンコーディング指定で読み込める(self, tmp_path: Path) -> None:
        """Shift-JISエンコーディングのCSVを読み込める。"""
        csv_path = tmp_path / "sjis.csv"
        df = pd.DataFrame({"名前": ["太郎", "花子"], "年齢": [25, 30]})
        df.to_csv(csv_path, index=False, encoding="shift_jis")
        result = load_csv(csv_path, encoding="shift_jis")
        assert list(result.columns) == ["名前", "年齢"]
        assert len(result) == 2

    def test_拡張子がcsv以外でValueError(self, tmp_path: Path) -> None:
        """CSV以外の拡張子のファイルを指定するとValueErrorが発生する。"""
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("a,b\n1,2\n")
        with pytest.raises(ValueError, match="CSV"):
            load_csv(txt_file)


class TestLoadCsvChunked:
    """load_csv_chunked 関数のテスト。"""

    def test_チャンク読み込みで全行取得(self, large_sample_csv: Path) -> None:
        """チャンク読み込みでも全行が結合されて返される。"""
        df = load_csv_chunked(large_sample_csv, chunk_size=200)
        assert len(df) == 1000

    def test_チャンク読み込みの列が正しい(self, large_sample_csv: Path) -> None:
        """チャンク読み込みでも列名が保持される。"""
        df = load_csv_chunked(large_sample_csv, chunk_size=500)
        assert list(df.columns) == ["id", "category", "value", "count"]
