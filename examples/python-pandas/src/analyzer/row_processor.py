"""行単位処理モジュール（ベクトル化演算版・ベストプラクティス）。

同じビジネスロジックを forループではなくベクトル化演算で実装する。
np.select() による条件分岐、ベクトル化算術演算による割引計算を用いて、
pandas本来のパフォーマンスを発揮する。

■ アンチパターン版（row_processor_antipattern.py）との違い
  - forループ + itertuples() → np.select() + ベクトル化演算
  - 1行ずつ関数を呼び出す → DataFrame全体に一括適用
  - list[dict] を返す → DataFrame を返す（pandas のエコシステムに沿う）

■ forループが本当に必要なケース（ベクトル化不可能な場合）
  - 行ごとに外部APIを呼び出す（HTTPリクエスト等）
  - 行ごとにDB書き込みを行う
  - 前の行の処理結果が次の行に影響する（再帰的依存）
  上記の場合のみ itertuples() を使う（row_processor_antipattern.py 参照）
"""

from enum import Enum

import numpy as np
import pandas as pd

__all__ = [
    "BULK_DISCOUNT_RATE",
    "BULK_QUANTITY_THRESHOLD",
    "HIGH_TOTAL_THRESHOLD",
    "MEMBER_DISCOUNT_RATE",
    "OrderPriority",
    "URGENT_TOTAL_THRESHOLD",
    "add_discounted_total",
    "add_order_priority",
    "process_orders",
]

MEMBER_DISCOUNT_RATE = 0.10
"""会員割引率（10%）。"""

BULK_DISCOUNT_RATE = 0.05
"""大量注文割引率（5%）。"""

BULK_QUANTITY_THRESHOLD = 50
"""大量注文とみなす最小数量。"""

URGENT_TOTAL_THRESHOLD = 10_000
"""urgent 判定の合計金額しきい値。"""

HIGH_TOTAL_THRESHOLD = 5_000
"""high 判定の合計金額しきい値。"""


class OrderPriority(Enum):
    """注文の優先度を表すドメイン型。"""

    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


_REQUIRED_COLUMNS = frozenset(
    {"order_id", "product_name", "quantity", "unit_price", "is_member"}
)


def _validate_columns(df: pd.DataFrame) -> None:
    """必須列の存在を検証する。"""
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"必須列が不足しています: {sorted(missing)}")


def add_order_priority(df: pd.DataFrame) -> pd.DataFrame:
    """注文の優先度列をベクトル化演算で追加する。

    np.select() を使い、全行の条件分岐を一括で処理する。
    forループや apply() は使わない。

    Args:
        df: 注文データのDataFrame。quantity, unit_price, is_member 列が必要。

    Returns:
        priority 列が追加された新しいDataFrame。
    """
    result = df.copy()
    total = result["quantity"] * result["unit_price"]

    conditions = [
        (result["quantity"] >= BULK_QUANTITY_THRESHOLD) & (total >= URGENT_TOTAL_THRESHOLD),
        total >= HIGH_TOTAL_THRESHOLD,
        result["is_member"].astype(bool),
    ]
    choices = [
        OrderPriority.URGENT.value,
        OrderPriority.HIGH.value,
        OrderPriority.NORMAL.value,
    ]

    result["priority"] = np.select(conditions, choices, default=OrderPriority.LOW.value)
    return result


def add_discounted_total(df: pd.DataFrame) -> pd.DataFrame:
    """割引適用後の合計金額列をベクトル化演算で追加する。

    条件ごとの割引率をベクトル化で算出し、合計金額に一括適用する。
    forループや apply() は使わない。

    Args:
        df: 注文データのDataFrame。unit_price, quantity, is_member 列が必要。

    Returns:
        discounted_total 列が追加された新しいDataFrame。
    """
    result = df.copy()
    total = result["unit_price"] * result["quantity"]

    discount_rate = pd.Series(0.0, index=result.index)
    discount_rate = discount_rate + np.where(result["is_member"], MEMBER_DISCOUNT_RATE, 0.0)
    discount_rate = discount_rate + np.where(result["quantity"] >= BULK_QUANTITY_THRESHOLD, BULK_DISCOUNT_RATE, 0.0)

    result["discounted_total"] = total * (1.0 - discount_rate)
    return result


def process_orders(df: pd.DataFrame) -> pd.DataFrame:
    """注文DataFrameに優先度と割引金額をベクトル化演算で一括追加する。

    メソッドチェインで add_order_priority → add_discounted_total を適用する。

    Args:
        df: 注文データのDataFrame。必須列: order_id, product_name,
            quantity, unit_price, is_member。

    Returns:
        priority, discounted_total 列が追加された新しいDataFrame。

    Raises:
        ValueError: 必須列が不足している場合。
    """
    _validate_columns(df)
    return df.pipe(add_order_priority).pipe(add_discounted_total)
