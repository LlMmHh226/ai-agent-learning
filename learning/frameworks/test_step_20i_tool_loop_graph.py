"""真实图、Reducer、ToolNode和业务函数；模型生成替换为本地模拟。"""

import json
import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError

from learning.frameworks import step_20i_tool_loop_graph as demo
from learning.frameworks import step_19d_langchain_tool_object as tool_module


class ToolLoopGraphTests(unittest.IsolatedAsyncioTestCase):
    def model(self):
        return ChatOpenAI(model="test", api_key="test-only", base_url="https://example.invalid")

    async def test_tool_roundtrip_and_message_merge(self):
        seen = []
        async def generate(model, messages, *args, **kwargs):
            seen.append(list(messages))
            if len(seen) == 1:
                reply = AIMessage(content="", tool_calls=[{
                    "name": "lookup_order", "args": {"order_id": "10001"}, "id": "call_graph",
                }])
            else:
                self.assertEqual(len(messages), 4)
                self.assertIsInstance(messages[-1], ToolMessage)
                self.assertEqual(messages[-1].tool_call_id, "call_graph")
                data = json.loads(messages[-1].content)
                self.assertEqual(data["tracking_number"], "SF1234567890")
                reply = AIMessage(content="模拟回答：" + data["tracking_number"])
            return ChatResult(generations=[ChatGeneration(message=reply)])
        with patch.object(ChatOpenAI, "_agenerate", new=generate), patch.object(tool_module, "get_order_status", wraps=tool_module.get_order_status) as business:
            graph = demo.build_graph(self.model())
            updates = [update async for update in graph.astream(demo.initial_input("查10001物流"), config={"recursion_limit": 6}, stream_mode="updates")]
            business.assert_called_once_with("10001")
        path = [name for update in updates for name in update]
        self.assertEqual(path, ["model", "tools", "model"])
        self.assertEqual(len(seen), 2)
        self.assertEqual(updates[-1]["model"]["messages"][0].content, "模拟回答：SF1234567890")
        print("实际图路径：", " → ".join(path))
        print("两次模型输入条数：", [len(messages) for messages in seen])

    async def test_no_tool_call_ends(self):
        async def generate(model, messages, *args, **kwargs):
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content="模拟问候：你好。"))])
        with patch.object(ChatOpenAI, "_agenerate", new=generate), patch.object(tool_module, "get_order_status") as business:
            result = await demo.build_graph(self.model()).ainvoke(demo.initial_input("你好"))
            business.assert_not_called()
        self.assertEqual(len(result["messages"]), 3)
        self.assertEqual(result["messages"][-1].content, "模拟问候：你好。")

    async def test_infinite_tool_requests_stop(self):
        calls = []
        async def generate(model, messages, *args, **kwargs):
            calls.append(1)
            reply = AIMessage(content="", tool_calls=[{
                "name": "lookup_order", "args": {"order_id": "10001"}, "id": f"loop_{len(calls)}",
            }])
            return ChatResult(generations=[ChatGeneration(message=reply)])
        with patch.object(ChatOpenAI, "_agenerate", new=generate):
            with self.assertRaises(GraphRecursionError):
                await demo.build_graph(self.model()).ainvoke(demo.initial_input("查10001"), config={"recursion_limit": 6})
        self.assertLessEqual(len(calls), 6)


if __name__ == "__main__":
    unittest.main()
