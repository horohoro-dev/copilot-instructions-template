"""CSVファイル読み込みモジュール。

CSVファイルの読み込み、バリデーション、型変換を行う。
大規模ファイルのチャンク読み込みにも対応する。
"""

from pathlib import Path

import pandas as pd


def load_csv(
    file_path: Path | str,
    dtypes: dict[str, str] | None = None,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """CSVファイルを読み込みDataFrameとして返す。

    ファイルの存在確認、拡張子チェック、空ファイルチェックを行った上で
    pandasでCSVを読み込む。dtypeを指定することでメモリ効率の良い
    型を利用できる。

    Args:
        file_path: CSVファイルのパス。
        dtypes: 列名をキー、dtype文字列を値とする辞書。
        encoding: ファイルのエンコーディング。

    Returns:
        読み込んだデータのDataFrame。

    Raises:
        FileNotFoundError: ファイルが存在しない場合。
        ValueError: ファイルが空またはCSV以外の拡張子の場合。

    Examples:
        >>> from pathlib import Path
        >>> df = load_csv(Path("sales.csv"), dtypes={"price": "float32"})
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError(f"CSVファイルのみ対応しています（拡張子: {file_path.suffix}）")

    if file_path.stat().st_size == 0:
        raise ValueError(f"空のファイルです: {file_path}")

    df = pd.read_csv(file_path, dtype=dtypes, encoding=encoding)
    return df


def load_csv_chunked(
    file_path: Path | str,
    chunk_size: int = 10000,
    dtypes: dict[str, str] | None = None,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """大規模CSVファイルをチャンク単位で読み込み結合して返す。

    メモリ使用量を抑えるため、指定されたチャンクサイズごとに
    読み込みを行い、最終的に結合したDataFrameを返す。

    Args:
        file_path: CSVファイルのパス。
        chunk_size: 一度に読み込む行数。
        dtypes: 列名をキー、dtype文字列を値とする辞書。
        encoding: ファイルのエンコーディング。

    Returns:
        全チャンクを結合したDataFrame。

    Examples:
        >>> df = load_csv_chunked("large_data.csv", chunk_size=5000)
    """
    file_path = Path(file_path)

    chunks: list[pd.DataFrame] = []
    reader = pd.read_csv(
        file_path, dtype=dtypes, encoding=encoding, chunksize=chunk_size
    )
    for chunk in reader:
        chunks.append(chunk)

    return pd.concat(chunks, ignore_index=True)
