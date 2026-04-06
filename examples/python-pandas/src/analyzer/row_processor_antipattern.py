"""行単位処理モジュール（ベストプラクティス実装）。

pandasのDataFrameを行単位で処理する必要がある場合の推奨パターンを示す。

■ 原則: ベクトル化演算を最優先で使う
  行単位のforループはパフォーマンスが大幅に劣化するため、
  外部API呼び出し・複雑な条件分岐など、ベクトル化が不可能な場合にのみ使用する。

■ iterrows() は使わない
  - 各行がSeriesに変換され、dtype情報が失われる
  - itertuples() の10倍以上遅い

■ itertuples() を使う場合のベストプラクティス
  1. NamedTupleで行の型を明示定義する
  2. ループ内で呼ぶ関数の引数に具体的な型ヒントを付ける（any/object禁止）
  3. index=False を指定して不要なIndex列を除外する

■ パフォーマンス目安（相対速度）
  ベクトル化演算:     1x（基準・最速）
  apply(axis=1):     10-100x 遅い
  リスト内包表記+zip: 10-50x 遅い
  itertuples():      50-100x 遅い
  iterrows():        500-1000x 遅い
"""

from enum import Enum
from typing import NamedTuple

import pandas as pd

__all__ = [
    "BULK_DISCOUNT_RATE",
    "BULK_QUANTITY_THRESHOLD",
    "HIGH_TOTAL_THRESHOLD",
    "MEMBER_DISCOUNT_RATE",
    "OrderPriority",
    "OrderRow",
    "URGENT_TOTAL_THRESHOLD",
    "apply_discount",
    "build_order_summary",
    "classify_order_priority",
    "process_orders_row_by_row",
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


class OrderRow(NamedTuple):
    """注文データ1行分の型定義。

    itertuples() から取り出した行データを型安全に扱うために使用する。
    すべてのフィールドに具体的な型を指定する（any/object は使わない）。
    """

    order_id: str
    product_name: str
    quantity: int
    unit_price: float
    is_member: bool


def classify_order_priority(
    quantity: int,
    unit_price: float,
    is_member: bool,
) -> OrderPriority:
    """注文の優先度を判定する。

    複雑な条件分岐を含むため、ベクトル化が困難なロジックの例。
    np.select() で書けなくもないが、可読性が著しく低下するケース。

    Args:
        quantity: 注文数量。
        unit_price: 単価。
        is_member: 会員かどうか。

    Returns:
        注文の優先度。
    """
    total = quantity * unit_price

    if quantity >= BULK_QUANTITY_THRESHOLD and total >= URGENT_TOTAL_THRESHOLD:
        return OrderPriority.URGENT
    if total >= HIGH_TOTAL_THRESHOLD:
        return OrderPriority.HIGH
    if is_member:
        return OrderPriority.NORMAL
    return OrderPriority.LOW


def apply_discount(
    unit_price: float,
    quantity: int,
    is_member: bool,
) -> float:
    """割引を適用した合計金額を算出する。

    Args:
        unit_price: 単価。
        quantity: 注文数量。
        is_member: 会員かどうか。

    Returns:
        割引適用後の合計金額。
    """
    total = unit_price * quantity
    discount_rate = 0.0

    if is_member:
        discount_rate += MEMBER_DISCOUNT_RATE

    if quantity >= BULK_QUANTITY_THRESHOLD:
        discount_rate += BULK_DISCOUNT_RATE

    return total * (1.0 - discount_rate)


def build_order_summary(
    order_id: str,
    product_name: str,
    quantity: int,
    discounted_total: float,
    priority: OrderPriority,
) -> dict[str, str | int | float | OrderPriority]:
    """注文サマリー辞書を構築する。

    Args:
        order_id: 注文ID。
        product_name: 商品名。
        quantity: 注文数量。
        discounted_total: 割引適用後の合計金額。
        priority: 優先度。

    Returns:
        注文サマリーの辞書。
    """
    return {
        "order_id": order_id,
        "product_name": product_name,
        "quantity": quantity,
        "discounted_total": discounted_total,
        "priority": priority,
    }


_REQUIRED_COLUMNS = frozenset(
    {"order_id", "product_name", "quantity", "unit_price", "is_member"}
)


def process_orders_row_by_row(
    df: pd.DataFrame,
) -> list[dict[str, str | int | float | OrderPriority]]:
    """注文DataFrameを行単位で処理し、サマリーリストを返す。

    itertuples(index=False) を使い、NamedTuple として各行を取り出す。
    各行に対して classify_order_priority() / apply_discount() を呼び出し、
    結果を build_order_summary() で辞書に組み立てる。

    ■ なぜ itertuples() を使うのか
      - iterrows() と異なり、dtypeが保持される
      - NamedTupleとして返されるため、属性アクセスが型安全
      - iterrows() の約10倍高速

    ■ なぜ for ループなのか
      このサンプルでは「各行ごとに外部関数を呼び出す」ユースケースを想定。
      外部API・DB書き込み・複雑な条件分岐など、ベクトル化できない処理がある場合にのみ使う。

    Args:
        df: 注文データのDataFrame。必須列: order_id, product_name,
            quantity, unit_price, is_member。

    Returns:
        各注文のサマリー辞書のリスト。

    Raises:
        ValueError: 必須列が不足している場合。
    """
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"必須列が不足しています: {sorted(missing)}")

    if df.empty:
        return []

    results: list[dict[str, str | int | float | OrderPriority]] = []

    for row in df.itertuples(index=False):
        order_id: str = str(row.order_id)
        product_name: str = str(row.product_name)
        quantity: int = int(row.quantity)
        unit_price: float = float(row.unit_price)
        is_member: bool = bool(row.is_member)

        priority = classify_order_priority(
            quantity=quantity,
            unit_price=unit_price,
            is_member=is_member,
        )

        discounted_total = apply_discount(
            unit_price=unit_price,
            quantity=quantity,
            is_member=is_member,
        )

        summary = build_order_summary(
            order_id=order_id,
            product_name=product_name,
            quantity=quantity,
            discounted_total=discounted_total,
            priority=priority,
        )
        results.append(summary)

    return results
