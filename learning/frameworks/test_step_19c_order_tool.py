"""本地模拟模型验证消息往返；实际复用本地FAKE_ORDERS查询函数。"""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, ToolMessage
from learning.frameworks import step_19c_langchain_order_tool as demo


class OrderToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_tool_result_returns_to_model(self):
        call_reply = AIMessage(content="", tool_calls=[{
            "name": "get_order_status", "args": {"order_id": "10001"}, "id": "call_test",
        }])
        bound = SimpleNamespace(ainvoke=AsyncMock(return_value=call_reply))
        async def finish(messages):
            self.assertEqual(len(messages), 4)
            self.assertIs(messages[2], call_reply)
            self.assertIsInstance(messages[3], ToolMessage)
            self.assertEqual(messages[3].tool_call_id, "call_test")
            result = json.loads(messages[3].content)
            self.assertEqual(result["tracking_number"], "SF1234567890")
            return AIMessage(content="模拟回答：" + result["tracking_number"])
        model = SimpleNamespace(bind_tools=lambda definitions: bound, ainvoke=AsyncMock(side_effect=finish))
        settings = SimpleNamespace(llm_model="test", llm_api_key="test-only", llm_base_url="https://example.invalid")
        with patch.object(demo, "get_settings", return_value=settings), patch.object(demo, "ChatOpenAI", return_value=model), patch("builtins.print"):
            self.assertEqual(await demo.ask_order("查10001"), "模拟回答：SF1234567890")
        self.assertEqual(bound.ainvoke.await_count, 1)
        self.assertEqual(model.ainvoke.await_count, 1)

    def test_invalid_calls_do_not_execute(self):
        cases = [
            {"name": "delete_order", "args": {"order_id": "10001"}},
            {"name": "get_order_status", "args": {}},
            {"name": "get_order_status", "args": {"order_id": 10001}},
            {"name": "get_order_status", "args": {"order_id": "10001", "extra": True}},
        ]
        with patch.object(demo, "get_order_status") as lookup:
            for call in cases:
                self.assertIn("error", demo.execute_order_call(call))
            lookup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
