# 课程：step_10_parameterized_test.md；访问范围：本地运行（无外部模型请求）。
"""
第 10 步：用多组参数测试同一个订单查询函数。

运行方式（在项目根目录下）：
    python -m unittest learning.steps_01_20.step_10_parameterized_test -v
"""

import unittest

from app.tools.order_tools import get_order_status


class OrderToolParameterizedTests(unittest.TestCase):
    def test_existing_orders(self) -> None:
        # 每个元组是一组输入和预期结果。
        cases = [
            ("10001", "已发货", "机械键盘", "SF1234567890"),
            ("10002", "待发货", "无线鼠标", ""),
            ("10003", "已完成", "显示器", "YT9876543210"),
        ]

        for order_id, expected_status, expected_product, expected_tracking in cases:
            # 如果某一组失败，测试报告会显示具体是哪个 order_id。
            with self.subTest(order_id=order_id):
                result = get_order_status(order_id)

                self.assertTrue(result["found"])
                self.assertEqual(result["order_id"], order_id)
                self.assertEqual(result["status"], expected_status)
                self.assertEqual(result["product"], expected_product)
                self.assertEqual(
                    result["tracking_number"],
                    expected_tracking,
                )

    def test_missing_orders(self) -> None:
        missing_order_ids = ["99999", "abc", "10004"]

        for order_id in missing_order_ids:
            with self.subTest(order_id=order_id):
                result = get_order_status(order_id)

                self.assertFalse(result["found"])
                self.assertEqual(result["message"], "没有找到该订单")


if __name__ == "__main__":
    unittest.main()
