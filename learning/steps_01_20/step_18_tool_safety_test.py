# 课程：step_18_tool_safety_test.md；访问范围：本地运行（无外部模型请求）。
"""
第 18 步：测试 Agent 的工具安全边界。

运行方式（在项目根目录下）：
    python -m unittest learning.steps_01_20.step_18_tool_safety_test -v
"""

import json
import unittest

from app.services.llm_service import LLMService


class ToolSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        # _execute_tool() 不需要模型客户端，因此不运行 LLMService.__init__()。
        self.service = object.__new__(LLMService)

    def test_unknown_tool_is_rejected(self) -> None:
        result = self.service._execute_tool(
            name="delete_all_orders",
            arguments="{}",
        )

        self.assertEqual(
            result,
            {"error": "不支持的工具：delete_all_orders"},
        )

    def test_missing_order_id_is_rejected(self) -> None:
        result = self.service._execute_tool(
            name="get_order_status",
            arguments="{}",
        )

        self.assertEqual(result, {"error": "订单查询参数无效"})

    def test_numeric_order_id_is_rejected(self) -> None:
        result = self.service._execute_tool(
            name="get_order_status",
            arguments=json.dumps({"order_id": 10001}),
        )

        self.assertEqual(
            result,
            {"error": "订单编号必须是字符串"},
        )

    def test_invalid_json_is_rejected(self) -> None:
        result = self.service._execute_tool(
            name="get_after_sales_policy",
            arguments="这不是JSON",
        )

        self.assertEqual(
            result,
            {"error": "售后政策查询参数无效"},
        )

    def test_valid_tool_request_still_works(self) -> None:
        result = self.service._execute_tool(
            name="get_order_status",
            arguments=json.dumps({"order_id": "10001"}),
        )

        self.assertTrue(result["found"])
        self.assertEqual(result["status"], "已发货")


if __name__ == "__main__":
    unittest.main()
