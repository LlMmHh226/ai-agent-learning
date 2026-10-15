# 课程：step_11_mock_model_test.md；访问范围：本地运行（无外部模型请求）。
"""
第 11 步：使用 AsyncMock 测试大模型服务。

运行方式（在项目根目录下）：
    python -m unittest learning.steps_01_20.step_11_mock_model_test -v
"""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.services.llm_service import LLMService


class LLMServiceMockTests(unittest.IsolatedAsyncioTestCase):
    async def test_normal_chat_without_real_api(self) -> None:
        # Arrange：准备一个与 SDK 返回结构相似的假响应。
        fake_message = SimpleNamespace(
            content="这是模拟的模型回答",
            tool_calls=[],
        )
        fake_response = SimpleNamespace(
            choices=[
                SimpleNamespace(message=fake_message),
            ]
        )

        # AsyncMock 模拟异步的 create() 方法。
        create_mock = AsyncMock(return_value=fake_response)

        service = LLMService()
        service.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=create_mock,
                )
            )
        )

        # Act：调用真正的 LLMService，但它内部访问的是假客户端。
        answer = await service.chat("你好")

        # Assert：检查服务返回值。
        self.assertEqual(answer, "这是模拟的模型回答")

        # 检查模型方法确实只被等待调用了一次。
        create_mock.assert_awaited_once()

        # 检查发送给假模型的用户消息。
        call_arguments = create_mock.await_args.kwargs
        messages = call_arguments["messages"]
        self.assertEqual(messages[-1]["role"], "user")
        self.assertEqual(messages[-1]["content"], "你好")


if __name__ == "__main__":
    unittest.main()
