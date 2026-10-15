import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.chat import llm_service
from main import app


class ChatApiRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch.object(
        llm_service,
        "chat",
        new_callable=AsyncMock,
    )
    def test_existing_chat_endpoint_still_works(
        self,
        chat_mock: AsyncMock,
    ) -> None:
        chat_mock.return_value = "原聊天接口正常"

        response = self.client.post(
            "/api/chat",
            json={"message": "你好"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "原聊天接口正常")
        self.assertEqual(response.json()["model"], llm_service.model)
        chat_mock.assert_awaited_once_with("你好")


if __name__ == "__main__":
    unittest.main()
