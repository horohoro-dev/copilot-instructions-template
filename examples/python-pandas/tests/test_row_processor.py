"""row_processor モジュールのテスト（ベクトル化演算版）。

同じビジネスロジックをベクトル化演算で実装した場合のテスト。
forループを使わず、np.select() とベクトル化算術演算で処理する。
"""

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from analyzer.row_processor import (
    OrderPriority,
    add_discounted_total,
    add_order_priority,
    process_orders,
)


@pytest.fixture
def orders_df() -> pd.DataFrame:
    """注文データのサンプルDataFrame。"""
    return pd.DataFrame(
        {
            "order_id": ["ORD-001", "ORD-002", "ORD-003", "ORD-004"],
            "product_name": ["Widget", "Gadget", "Thingamajig", "Doohickey"],
            "quantity": [10, 50, 2, 1],
            "unit_price": [150.0, 100.0, 5000.0, 50.0],
            "is_member": [True, False, True, False],
        }
    )


class TestOrderPriority:
    """OrderPriority Enum のテスト。"""

    def test_全優先度が定義されている(self) -> None:
        assert OrderPriority.URGENT.value == "urgent"
        assert OrderPriority.HIGH.value == "high"
        assert OrderPriority.NORMAL.value == "normal"
        assert OrderPriority.LOW.value == "low"


class TestAddOrderPriority:
    """add_order_priority 関数のテスト。

    np.select() によるベクトル化された優先度分類。
    """

    def test_priority列が追加される(self, orders_df: pd.DataFrame) -> None:
        result = add_order_priority(orders_df)
        assert "priority" in result.columns

    def test_元のDataFrameは変更されない(self, orders_df: pd.DataFrame) -> None:
        original_cols = list(orders_df.columns)
        add_order_priority(orders_df)
        assert list(orders_df.columns) == original_cols

    def test_高額かつ大量注文はURGENT(self) -> None:
        """quantity>=50 かつ total>=10000 → URGENT。"""
        df = pd.DataFrame(
            {"quantity": [100], "unit_price": [500.0], "is_member": [False]}
        )
        result = add_order_priority(df)
        assert result["priority"].iloc[0] == OrderPriority.URGENT.value

    def test_高額注文はHIGH(self) -> None:
        """total>=5000 → HIGH。"""
        df = pd.DataFrame(
            {"quantity": [5], "unit_price": [1000.0], "is_member": [False]}
        )
        result = add_order_priority(df)
        assert result["priority"].iloc[0] == OrderPriority.HIGH.value

    def test_会員の通常注文はNORMAL(self) -> None:
        df = pd.DataFrame(
            {"quantity": [3], "unit_price": [100.0], "is_member": [True]}
        )
        result = add_order_priority(df)
        assert result["priority"].iloc[0] == OrderPriority.NORMAL.value

    def test_非会員の少量低額注文はLOW(self) -> None:
        df = pd.DataFrame(
            {"quantity": [1], "unit_price": [50.0], "is_member": [False]}
        )
        result = add_order_priority(df)
        assert result["priority"].iloc[0] == OrderPriority.LOW.value

    def test_全行にベクトル化で適用される(self, orders_df: pd.DataFrame) -> None:
        """4行すべてが一括で処理される。"""
        result = add_order_priority(orders_df)
        expected = pd.Series(
            [
                OrderPriority.NORMAL.value,   # ORD-001: 会員, total=1500
                OrderPriority.HIGH.value,     # ORD-002: 非会員, qty=50, total=5000
                OrderPriority.HIGH.value,     # ORD-003: 会員, total=10000
                OrderPriority.LOW.value,      # ORD-004: 非会員, total=50
            ],
            name="priority",
        )
        assert_series_equal(result["priority"], expected)


class TestAddDiscountedTotal:
    """add_discounted_total 関数のテスト。

    ベクトル化算術演算による割引計算。
    """

    def test_discounted_total列が追加される(self, orders_df: pd.DataFrame) -> None:
        result = add_discounted_total(orders_df)
        assert "discounted_total" in result.columns

    def test_元のDataFrameは変更されない(self, orders_df: pd.DataFrame) -> None:
        original_cols = list(orders_df.columns)
        add_discounted_total(orders_df)
        assert list(orders_df.columns) == original_cols

    def test_会員割引10パーセント(self) -> None:
        df = pd.DataFrame(
            {"unit_price": [1000.0], "quantity": [2], "is_member": [True]}
        )
        result = add_discounted_total(df)
        assert result["discounted_total"].iloc[0] == pytest.approx(1800.0)

    def test_非会員は割引なし(self) -> None:
        df = pd.DataFrame(
            {"unit_price": [1000.0], "quantity": [2], "is_member": [False]}
        )
        result = add_discounted_total(df)
        assert result["discounted_total"].iloc[0] == pytest.approx(2000.0)

    def test_大量注文は追加5パーセント割引(self) -> None:
        df = pd.DataFrame(
            {"unit_price": [100.0], "quantity": [50], "is_member": [False]}
        )
        result = add_discounted_total(df)
        assert result["discounted_total"].iloc[0] == pytest.approx(4750.0)

    def test_会員かつ大量注文は15パーセント割引(self) -> None:
        df = pd.DataFrame(
            {"unit_price": [100.0], "quantity": [50], "is_member": [True]}
        )
        result = add_discounted_total(df)
        assert result["discounted_total"].iloc[0] == pytest.approx(4250.0)

    def test_全行にベクトル化で適用される(self, orders_df: pd.DataFrame) -> None:
        result = add_discounted_total(orders_df)
        expected = pd.Series(
            [
                1500.0 * 0.90,  # ORD-001: 会員, qty<50
                5000.0 * 0.95,  # ORD-002: 非会員, qty=50
                10000.0 * 0.90,  # ORD-003: 会員, qty<50
                50.0,           # ORD-004: 非会員, qty<50
            ],
            name="discounted_total",
        )
        assert_series_equal(result["discounted_total"], expected)


class TestProcessOrders:
    """process_orders 関数のテスト。

    priority と discounted_total を一括でベクトル化処理する統合関数。
    """

    def test_priority列とdiscounted_total列が追加される(
        self, orders_df: pd.DataFrame
    ) -> None:
        result = process_orders(orders_df)
        assert "priority" in result.columns
        assert "discounted_total" in result.columns

    def test_元の列は保持される(self, orders_df: pd.DataFrame) -> None:
        result = process_orders(orders_df)
        for col in orders_df.columns:
            assert col in result.columns

    def test_元のDataFrameは変更されない(self, orders_df: pd.DataFrame) -> None:
        original_cols = list(orders_df.columns)
        process_orders(orders_df)
        assert list(orders_df.columns) == original_cols

    def test_空のDataFrameでも列が追加される(self) -> None:
        empty_df = pd.DataFrame(
            columns=["order_id", "product_name", "quantity", "unit_price", "is_member"]
        )
        result = process_orders(empty_df)
        assert "priority" in result.columns
        assert "discounted_total" in result.columns
        assert len(result) == 0

    def test_必須列が不足している場合はValueError(self) -> None:
        bad_df = pd.DataFrame({"order_id": ["ORD-001"], "quantity": [10]})
        with pytest.raises(ValueError, match="必須列が不足"):
            process_orders(bad_df)

    def test_統合処理の結果が正しい(self, orders_df: pd.DataFrame) -> None:
        result = process_orders(orders_df)
        assert result.loc[0, "priority"] == OrderPriority.NORMAL.value
        assert result.loc[0, "discounted_total"] == pytest.approx(1350.0)
        assert result.loc[1, "priority"] == OrderPriority.HIGH.value
        assert result.loc[1, "discounted_total"] == pytest.approx(4750.0)
