"""模型响应模拟，工具包装/校验/本地业务执行和消息对象真实运行。"""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from learning.frameworks import step_19e_tool_object_roundtrip as demo
from learning.frameworks import step_19d_langchain_tool_object as tool_module


class ToolObjectTests(unittest.IsolatedAsyncioTestCase):
    def test_real_binding_schema_without_network(self):
        model = ChatOpenAI(model="test", api_key="test-only", base_url="https://example.invalid")
        bound = model.bind_tools([demo.lookup_order])
        schema = bound.kwargs["tools"][0]["function"]
        self.assertEqual(schema["name"], "lookup_order")
        self.assertIn("order_id", schema["parameters"]["required"])

    async def test_messages_and_real_tool_execution(self):
        reply = AIMessage(content="", tool_calls=[{
            "name": "lookup_order", "args": {"order_id": "10001"}, "id": "call_19e",
        }])
        bound = SimpleNamespace(ainvoke=AsyncMock(return_value=reply))
        async def finish(messages):
            self.assertEqual(len(messages), 4)
            self.assertIs(messages[2], reply)
            self.assertIsInstance(messages[3], ToolMessage)
            self.assertEqual(messages[3].tool_call_id, "call_19e")
            data = json.loads(messages[3].content)
            self.assertEqual(data["tracking_number"], "SF1234567890")
            return AIMessage(content="模拟回答：" + data["tracking_number"])
        model = SimpleNamespace(bind_tools=Mock(return_value=bound), ainvoke=AsyncMock(side_effect=finish))
        settings = SimpleNamespace(llm_model="test", llm_api_key="test-only", llm_base_url="https://example.invalid")
        with patch.object(demo, "get_settings", return_value=settings), patch.object(demo, "ChatOpenAI", return_value=model):
            self.assertEqual(await demo.ask_order("查10001物流"), "模拟回答：SF1234567890")
        model.bind_tools.assert_called_once_with([demo.lookup_order])
        self.assertEqual(bound.ainvoke.await_count, 1)
        self.assertEqual(model.ainvoke.await_count, 1)

    def test_invalid_requests_do_not_run_business(self):
        cases = [
            {"name": "get_order_status", "args": {"order_id": "10001"}},
            {"name": "lookup_order", "args": {}},
            {"name": "lookup_order", "args": {"order_id": 10001}},
            {"name": "lookup_order", "args": {"order_id": "10001", "extra": True}},
        ]
        with patch.object(tool_module, "get_order_status") as business:
            for call in cases:
                self.assertIn("error", demo.execute_tool_object(call))
            business.assert_not_called()


if __name__ == "__main__":
    unittest.main()
