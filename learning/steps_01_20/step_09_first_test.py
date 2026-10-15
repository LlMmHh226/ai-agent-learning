# 课程：step_09_first_test.md；访问范围：本地运行（无外部模型请求）。
"""
第 9 步：为订单查询函数编写第一个自动化测试。

运行方式（在项目根目录下）：
    python -m unittest learning.steps_01_20.step_09_first_test -v
"""

import unittest

from app.tools.order_tools import get_order_status


class OrderToolTests(unittest.TestCase):
    def test_existing_order(self) -> None:
        # Arrange（准备）：确定要查询的订单编号。
        order_id = "10001"

        # Act（执行）：调用需要测试的函数。
        result = get_order_status(order_id)

        # Assert（断言）：检查实际结果是否符合预期。
        self.assertTrue(result["found"])
        self.assertEqual(result["order_id"], "10001")
        self.assertEqual(result["status"], "已发货")
        self.assertEqual(result["product"], "机械键盘")
        self.assertEqual(result["tracking_number"], "SF1234567890")

    def test_missing_order(self) -> None:
        result = get_order_status("99999")

        self.assertFalse(result["found"])
        self.assertEqual(result["message"], "没有找到该订单")


if __name__ == "__main__":
    unittest.main()
