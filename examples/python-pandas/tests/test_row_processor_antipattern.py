"""row_processor_antipattern モジュールのテスト。

行単位の処理が避けられない場合の次善策を検証する。
itertuples() + NamedTuple による型安全な行イテレーション（アンチパターン例）。
"""

import pandas as pd
import pytest

from analyzer.row_processor_antipattern import (
    OrderPriority,
    OrderRow,
    apply_discount,
    build_order_summary,
    classify_order_priority,
    process_orders_row_by_row,
)


class TestOrderRow:
    """OrderRow NamedTuple の型定義テスト。"""

    def test_フィールドが正しく定義されている(self) -> None:
        """OrderRowのフィールド名と型アノテーションが正しい。"""
        row = OrderRow(
            order_id="ORD-001",
            product_name="Widget",
            quantity=10,
            unit_price=150.0,
            is_member=True,
        )
        assert row.order_id == "ORD-001"
        assert row.product_name == "Widget"
        assert row.quantity == 10
        assert row.unit_price == 150.0
        assert row.is_member is True

    def test_フィールドの型アノテーションが明示的(self) -> None:
        """型アノテーションが any や object ではなく具体的な型である。"""
        annotations = OrderRow.__annotations__
        assert annotations["order_id"] is str
        assert annotations["product_name"] is str
        assert annotations["quantity"] is int
        assert annotations["unit_price"] is float
        assert annotations["is_member"] is bool


class TestOrderPriority:
    """OrderPriority Enum のテスト。"""

    def test_全優先度が定義されている(self) -> None:
        assert OrderPriority.URGENT.value == "urgent"
        assert OrderPriority.HIGH.value == "high"
        assert OrderPriority.NORMAL.value == "normal"
        assert OrderPriority.LOW.value == "low"


class TestClassifyOrderPriority:
    """classify_order_priority 関数のテスト。

    ベクトル化できない複雑な分岐ロジックを持つ関数。
    引数はすべて明示的な型を持つ。
    """

    def test_高額かつ大量注文はurgent(self) -> None:
        result = classify_order_priority(
            quantity=100, unit_price=500.0, is_member=False
        )
        assert result is OrderPriority.URGENT

    def test_会員の高額注文はhigh(self) -> None:
        result = classify_order_priority(
            quantity=5, unit_price=1000.0, is_member=True
        )
        assert result is OrderPriority.HIGH

    def test_非会員の高額注文はhigh(self) -> None:
        result = classify_order_priority(
            quantity=5, unit_price=1000.0, is_member=False
        )
        assert result is OrderPriority.HIGH

    def test_会員の通常注文はnormal(self) -> None:
        result = classify_order_priority(
            quantity=3, unit_price=100.0, is_member=True
        )
        assert result is OrderPriority.NORMAL

    def test_非会員の少量低額注文はlow(self) -> None:
        result = classify_order_priority(
            quantity=1, unit_price=50.0, is_member=False
        )
        assert result is OrderPriority.LOW


class TestApplyDiscount:
    """apply_discount 関数のテスト。

    会員情報と注文金額に応じた割引計算。
    引数はすべて明示的な型。
    """

    def test_会員は10パーセント割引(self) -> None:
        result = apply_discount(
            unit_price=1000.0, quantity=2, is_member=True
        )
        assert result == pytest.approx(1800.0)  # 2000 * 0.9

    def test_非会員は割引なし(self) -> None:
        result = apply_discount(
            unit_price=1000.0, quantity=2, is_member=False
        )
        assert result == pytest.approx(2000.0)

    def test_大量注文は追加5パーセント割引(self) -> None:
        """quantity >= 50 で追加5%割引。"""
        result = apply_discount(
            unit_price=100.0, quantity=50, is_member=False
        )
        assert result == pytest.approx(4750.0)  # 5000 * 0.95

    def test_会員かつ大量注文は両方の割引を適用(self) -> None:
        """会員10% + 大量注文5% = 合計15%割引。"""
        result = apply_discount(
            unit_price=100.0, quantity=50, is_member=True
        )
        assert result == pytest.approx(4250.0)  # 5000 * 0.85


class TestBuildOrderSummary:
    """build_order_summary 関数のテスト。

    行データから辞書を組み立てる関数。
    引数はすべて明示的な型。
    """

    def test_サマリー辞書を正しく構築(self) -> None:
        result = build_order_summary(
            order_id="ORD-001",
            product_name="Widget",
            quantity=10,
            discounted_total=1350.0,
            priority=OrderPriority.HIGH,
        )
        assert result == {
            "order_id": "ORD-001",
            "product_name": "Widget",
            "quantity": 10,
            "discounted_total": 1350.0,
            "priority": OrderPriority.HIGH,
        }


class TestProcessOrdersRowByRow:
    """process_orders_row_by_row 関数のテスト。

    itertuples() を使ってDataFrameの行を型安全にイテレートし、
    各行に対して外部関数を呼び出すパターンのテスト。
    """

    @pytest.fixture
    def orders_df(self) -> pd.DataFrame:
        """注文データのサンプルDataFrame。"""
        return pd.DataFrame(
            {
                "order_id": ["ORD-001", "ORD-002", "ORD-003"],
                "product_name": ["Widget", "Gadget", "Thingamajig"],
                "quantity": [10, 50, 2],
                "unit_price": [150.0, 100.0, 5000.0],
                "is_member": [True, False, True],
            }
        )

    def test_全行が処理される(self, orders_df: pd.DataFrame) -> None:
        results = process_orders_row_by_row(orders_df)
        assert len(results) == 3

    def test_各行のorder_idが保持される(self, orders_df: pd.DataFrame) -> None:
        results = process_orders_row_by_row(orders_df)
        order_ids = [r["order_id"] for r in results]
        assert order_ids == ["ORD-001", "ORD-002", "ORD-003"]

    def test_会員割引が適用される(self, orders_df: pd.DataFrame) -> None:
        """ORD-001: 会員、10個、150円 → 1500 * 0.9 = 1350.0。"""
        results = process_orders_row_by_row(orders_df)
        assert results[0]["discounted_total"] == pytest.approx(1350.0)

    def test_大量注文割引が適用される(self, orders_df: pd.DataFrame) -> None:
        """ORD-002: 非会員、50個、100円 → 5000 * 0.95 = 4750.0。"""
        results = process_orders_row_by_row(orders_df)
        assert results[1]["discounted_total"] == pytest.approx(4750.0)

    def test_会員かつ高額注文の優先度(self, orders_df: pd.DataFrame) -> None:
        """ORD-003: 会員、2個、5000円 → priority=HIGH。"""
        results = process_orders_row_by_row(orders_df)
        assert results[2]["priority"] is OrderPriority.HIGH

    def test_空のDataFrameは空リストを返す(self) -> None:
        empty_df = pd.DataFrame(
            columns=["order_id", "product_name", "quantity", "unit_price", "is_member"]
        )
        results = process_orders_row_by_row(empty_df)
        assert results == []

    def test_必須列が不足している場合はValueError(self) -> None:
        bad_df = pd.DataFrame({"order_id": ["ORD-001"], "quantity": [10]})
        with pytest.raises(ValueError, match="必須列が不足"):
            process_orders_row_by_row(bad_df)
