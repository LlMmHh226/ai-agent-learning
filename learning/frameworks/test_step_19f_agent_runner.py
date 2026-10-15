"""运行真实Agent与工具，仅替换模型生成方法，不请求网络。"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError

from learning.frameworks import step_19f_agent_runner as demo
from learning.frameworks import step_19d_langchain_tool_object as tool_module


class AgentRunnerTests(unittest.IsolatedAsyncioTestCase):
    def settings(self):
        return SimpleNamespace(llm_model="test", llm_api_key="test-only", llm_base_url="https://example.invalid")

    async def test_runner_executes_tool_and_returns_answer(self):
        observed = []
        async def fake_generate(model, messages, *args, **kwargs):
            observed.append(list(messages))
            if len(observed) == 1:
                self.assertEqual(kwargs["tools"][0]["function"]["name"], "lookup_order")
                reply = AIMessage(content="", tool_calls=[{
                    "name": "lookup_order", "args": {"order_id": "10001"}, "id": "call_runner",
                }])
            else:
                self.assertIsInstance(messages[-1], ToolMessage)
                self.assertEqual(messages[-1].tool_call_id, "call_runner")
                data = json.loads(messages[-1].content)
                self.assertEqual(data["tracking_number"], "SF1234567890")
                reply = AIMessage(content="模拟回答：" + data["tracking_number"])
            return ChatResult(generations=[ChatGeneration(message=reply)])
        with (
            patch.object(demo, "get_settings", return_value=self.settings()),
            patch.object(ChatOpenAI, "_agenerate", new=fake_generate),
            patch.object(tool_module, "get_order_status", wraps=tool_module.get_order_status) as business,
        ):
            self.assertEqual(await demo.ask_agent("查10001物流"), "模拟回答：SF1234567890")
            business.assert_called_once_with("10001")
        self.assertEqual(len(observed), 2)

    async def test_repeated_tool_requests_are_bounded(self):
        calls = []
        async def never_finish(model, messages, *args, **kwargs):
            calls.append(1)
            reply = AIMessage(content="", tool_calls=[{
                "name": "lookup_order", "args": {"order_id": "10001"}, "id": f"call_{len(calls)}",
            }])
            return ChatResult(generations=[ChatGeneration(message=reply)])
        with patch.object(demo, "get_settings", return_value=self.settings()), patch.object(ChatOpenAI, "_agenerate", new=never_finish):
            with self.assertRaises(GraphRecursionError):
                await demo.ask_agent("查10001物流")
        self.assertGreater(len(calls), 1)
        self.assertLessEqual(len(calls), 6)


if __name__ == "__main__":
    unittest.main()
