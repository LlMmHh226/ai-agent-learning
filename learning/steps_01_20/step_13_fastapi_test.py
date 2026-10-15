# 课程：step_13_fastapi_test.md；访问范围：本地运行（无外部模型请求）。
"""
第 13 步：使用 TestClient 测试 FastAPI 接口。

运行方式（在项目根目录下）：
    python -m unittest learning.steps_01_20.step_13_fastapi_test -v
"""

import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.services.llm_service import llm_service
from main import app


class ChatAPITests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch.object(llm_service, "chat", new_callable=AsyncMock)
    def test_chat_returns_answer_and_model(
        self,
        chat_mock: AsyncMock,
    ) -> None:
        # Arrange：让假模型固定返回一句话。
        chat_mock.return_value = "这是测试回答"

        # Act：像前端一样发送 HTTP 请求。
        response = self.client.post(
            "/api/chat",
            json={"message": "你好"},
        )

        # Assert：检查 HTTP 状态码和响应 JSON。
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "answer": "这是测试回答",
                "model": llm_service.model,
            },
        )
        chat_mock.assert_awaited_once_with("你好")

    @patch.object(llm_service, "chat", new_callable=AsyncMock)
    def test_blank_message_is_rejected_before_model_call(
        self,
        chat_mock: AsyncMock,
    ) -> None:
        response = self.client.post(
            "/api/chat",
            json={"message": "   "},
        )

        self.assertEqual(response.status_code, 422)
        chat_mock.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
