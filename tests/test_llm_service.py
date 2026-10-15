import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.services.llm_service import LLMService


class FakeAssistantMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none=True):
        result = {"role": "assistant"}
        if self.content is not None:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in self.tool_calls
            ]
        return result


def make_response(message):
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class LLMServiceToolTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.service = object.__new__(LLMService)
        self.service.model = "test-model"
        self.service.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=AsyncMock())
            )
        )

    def test_execute_order_tool(self):
        result = self.service._execute_tool(
            "get_order_status",
            json.dumps({"order_id": "10001"}),
        )
        self.assertTrue(result["found"])
        self.assertEqual(result["status"], "已发货")

    def test_execute_tool_rejects_invalid_arguments(self):
        result = self.service._execute_tool("get_order_status", "not-json")
        self.assertEqual(result, {"error": "订单查询参数无效"})

    def test_execute_policy_tool(self):
        result = self.service._execute_tool(
            "get_after_sales_policy",
            json.dumps({"topic": "退款"}),
        )
        self.assertTrue(result["found"])
        self.assertEqual(result["topic"], "退款")
        self.assertIn("1至3个工作日", result["policy"])

    def test_execute_knowledge_tool(self):
        result = self.service._execute_tool(
            "search_knowledge_base",
            json.dumps({"query": "星云机械键盘支持热插拔吗？"}),
        )
        self.assertTrue(result["found"])
        first_result = result["results"][0]
        self.assertEqual(first_result["source"], "products.md")
        self.assertIn("五脚轴热插拔", first_result["snippet"])

    async def test_chat_completes_tool_call_loop(self):
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="get_order_status",
                arguments=json.dumps({"order_id": "10001"}),
            ),
        )
        self.service.client.chat.completions.create.side_effect = [
            make_response(FakeAssistantMessage(tool_calls=[tool_call])),
            make_response(FakeAssistantMessage(content="订单10001已发货。")),
        ]

        answer = await self.service.chat_with_messages(
            [{"role": "user", "content": "查询订单10001"}]
        )

        self.assertEqual(answer, "订单10001已发货。")
        second_call_messages = (
            self.service.client.chat.completions.create.call_args_list[1]
            .kwargs["messages"]
        )
        self.assertEqual(second_call_messages[-1]["role"], "tool")
        self.assertIn("已发货", second_call_messages[-1]["content"])

    async def test_chat_completes_knowledge_tool_call_loop(self):
        tool_call = SimpleNamespace(
            id="call-knowledge-1",
            function=SimpleNamespace(
                name="search_knowledge_base",
                arguments=json.dumps(
                    {"query": "星云机械键盘支持热插拔吗？"},
                    ensure_ascii=False,
                ),
            ),
        )
        self.service.client.chat.completions.create.side_effect = [
            make_response(FakeAssistantMessage(tool_calls=[tool_call])),
            make_response(
                FakeAssistantMessage(
                    content=(
                        "支持五脚轴热插拔。"
                        "来源：products.md，products.md#chunk-0。"
                    )
                )
            ),
        ]

        answer = await self.service.chat_with_messages(
            [{"role": "user", "content": "星云机械键盘支持热插拔吗？"}]
        )

        self.assertIn("支持五脚轴热插拔", answer)
        self.assertIn("products.md#chunk-0", answer)
        second_call_messages = (
            self.service.client.chat.completions.create.call_args_list[1]
            .kwargs["messages"]
        )
        tool_message = second_call_messages[-1]
        self.assertEqual(tool_message["role"], "tool")
        self.assertEqual(tool_message["tool_call_id"], "call-knowledge-1")
        self.assertIn("products.md#chunk-0", tool_message["content"])


if __name__ == "__main__":
    unittest.main()
