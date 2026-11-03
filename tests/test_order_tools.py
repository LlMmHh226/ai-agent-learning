import unittest
from unittest.mock import patch

from app.repositories.order_repository import OrderRepositoryError
from app.tools.order_tools import get_order_status


class OrderToolTests(unittest.TestCase):
    @patch("app.tools.order_tools.fetch_order_from_db")
    def test_found_order_keeps_tool_response_contract(self, lookup) -> None:
        lookup.return_value = {
            "order_id": "db-only-order",
            "status": "待发货",
            "product": "数据库订单商品",
            "tracking_number": "",
        }

        result = get_order_status("db-only-order")

        self.assertEqual(
            result,
            {"found": True, **lookup.return_value},
        )
        lookup.assert_called_once_with("db-only-order")

    @patch("app.tools.order_tools.fetch_order_from_db", return_value=None)
    def test_missing_order_keeps_not_found_response(self, _lookup) -> None:
        self.assertEqual(
            get_order_status("missing-order"),
            {"found": False, "message": "没有找到该订单"},
        )

    @patch(
        "app.tools.order_tools.fetch_order_from_db",
        side_effect=OrderRepositoryError("database unavailable"),
    )
    def test_database_failure_is_not_reported_as_missing_order(self, _lookup) -> None:
        with self.assertLogs("app.tools.order_tools", level="ERROR"):
            result = get_order_status("10001")

        self.assertEqual(result, {"error": "订单查询服务暂时不可用，请稍后重试"})
        self.assertNotIn("found", result)


if __name__ == "__main__":
    unittest.main()
