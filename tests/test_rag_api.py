import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.rag import rag_service
from app.services.rag_service import RAGResult, RAGSource
from main import app


class RAGApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch.object(
        rag_service,
        "chat",
        new_callable=AsyncMock,
    )
    def test_returns_answer_and_sources(
        self,
        chat_mock: AsyncMock,
    ) -> None:
        chat_mock.return_value = RAGResult(
            answer="请联系人工客服核查。",
            sources=[
                RAGSource(
                    source="shipping.md",
                    chunk_id="shipping.md#chunk-0",
                    snippet="物流超过48小时没有更新时联系人工客服。",
                )
            ],
        )

        response = self.client.post(
            "/api/rag/chat",
            json={"message": "物流没更新怎么办？"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "answer": "请联系人工客服核查。",
                "sources": [
                    {
                        "source": "shipping.md",
                        "chunk_id": "shipping.md#chunk-0",
                        "snippet": "物流超过48小时没有更新时联系人工客服。",
                    }
                ],
            },
        )
        chat_mock.assert_awaited_once_with(query="物流没更新怎么办？")

    def test_reuses_chat_request_validation(self) -> None:
        response = self.client.post(
            "/api/rag/chat",
            json={"message": "   "},
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
