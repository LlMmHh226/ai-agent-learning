import unittest
from unittest.mock import AsyncMock, patch

from app.rag.prompt_builder import RAG_INSUFFICIENT_CONTEXT_RESPONSE
from app.services.llm_service import llm_service
from app.services.rag_service import RAGService


class RAGServiceTests(unittest.IsolatedAsyncioTestCase):
    @patch.object(
        llm_service,
        "complete_messages",
        new_callable=AsyncMock,
    )
    async def test_retrieves_context_before_model_call(
        self,
        complete_mock: AsyncMock,
    ) -> None:
        complete_mock.return_value = "请联系人工客服核查。"
        service = RAGService()

        result = await service.chat(
            "物流轨迹超过 48 小时没有更新怎么办？"
        )

        self.assertEqual(result.answer, "请联系人工客服核查。")
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0].source, "shipping.md")
        self.assertEqual(
            result.sources[0].chunk_id,
            "shipping.md#chunk-0",
        )
        self.assertIn("超过 48 小时", result.sources[0].snippet)
        messages = complete_mock.await_args.kwargs["messages"]
        self.assertIn("shipping.md#chunk-0", messages[1]["content"])
        self.assertIn("超过 48 小时", messages[1]["content"])

    @patch.object(
        llm_service,
        "complete_messages",
        new_callable=AsyncMock,
    )
    async def test_rejects_weak_match_without_model_call(
        self,
        complete_mock: AsyncMock,
    ) -> None:
        service = RAGService(min_score=0.3)

        result = await service.chat("商品有优惠券吗？")

        self.assertEqual(result.answer, RAG_INSUFFICIENT_CONTEXT_RESPONSE)
        self.assertEqual(result.sources, [])
        complete_mock.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
